"""Async orchestrator: schedule attack × rule × condition trials with a
semaphore-bounded concurrency pool.

Pattern lifted from bloom (`src/bloom/stages/step3_rollout.py:285-361`),
adapted to single-turn evaluations: each "trial" is at most two LLM calls
(judge_input → target → judge_output), not a multi-turn conversation.

A trial is one row in the result JSON. The orchestrator never aggregates
or scores; it only produces raw per-trial records.
"""
from __future__ import annotations
import asyncio
import json
import time
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, List, Dict, Any

from .attacks import Attack
from .rules import Rule
from .judges import JudgeVariant, render_judge_prompt, parse_verdict
from .client import OpenRouterClient, ChatResult, estimate_cost
from . import config


@dataclass
class TrialResult:
    attack_id: str
    attack_category: str
    attack_source: str
    rule_id: str
    judge_variant: str
    judge_placement: str       # "none" | "input" | "output"
    target_model: str
    judge_model: str
    rendered_input: str
    target_response: Optional[str]
    target_finish_reason: Optional[str]
    judge_input_text: Optional[str]
    judge_input_verdict: Optional[str]   # "ALLOW" | "BLOCK" | None
    judge_output_text: Optional[str]
    judge_output_verdict: Optional[str]
    final_action: str          # "delivered" | "blocked_input" | "blocked_output"
    rule_violated: bool        # only if delivered, otherwise False
    cost_usd: float
    latency_s: float
    target_prompt_tokens: int = 0
    target_completion_tokens: int = 0
    judge_prompt_tokens: int = 0
    judge_completion_tokens: int = 0
    error: Optional[str] = None


@dataclass
class Plan:
    attack: Attack
    rule: Rule
    judge: JudgeVariant
    placement: str   # "none" | "input" | "output"


def build_plans(attacks: List[Attack], rules: List[Rule],
                judges: List[JudgeVariant]) -> List[Plan]:
    plans: List[Plan] = []
    for atk in attacks:
        for rule in rules:
            for j in judges:
                if not j.has_judge:
                    plans.append(Plan(atk, rule, j, "none"))
                else:
                    plans.append(Plan(atk, rule, j, "input"))
                    plans.append(Plan(atk, rule, j, "output"))
    return plans


async def _run_one(client: OpenRouterClient, plan: Plan, target_model: str) -> TrialResult:
    attack, rule, judge, placement = plan.attack, plan.rule, plan.judge, plan.placement
    rendered_input = attack.render(rule.objective)

    t0 = time.perf_counter()
    judge_in_text = None
    judge_in_verdict = None
    judge_out_text = None
    judge_out_verdict = None
    target_response = None
    target_finish = None
    target_prompt_tokens = 0
    target_completion_tokens = 0
    judge_prompt_tokens = 0
    judge_completion_tokens = 0
    cost_usd = 0.0
    final_action = "delivered"
    rule_violated = False
    err: Optional[str] = None

    try:
        # 1) input-side judge (if applicable)
        if placement == "input":
            jp = render_judge_prompt(judge.id, "input", rule.system_prompt,
                                     rendered_input, None)
            jr = await client.chat_with_retry(
                model=config.JUDGE_MODEL,
                system=None,
                user=jp,
                max_tokens=config.MAX_JUDGE_TOKENS,
                temperature=config.TEMPERATURE_JUDGE,
            )
            judge_in_text = jr.text
            judge_in_verdict = parse_verdict(jr.text)
            judge_prompt_tokens += jr.prompt_tokens
            judge_completion_tokens += jr.completion_tokens
            cost_usd += estimate_cost(config.JUDGE_MODEL, jr.prompt_tokens, jr.completion_tokens)
            if judge_in_verdict == "BLOCK":
                final_action = "blocked_input"

        # 2) target call (always, unless input-side blocked)
        if final_action == "delivered":
            tr = await client.chat_with_retry(
                model=target_model,
                system=rule.system_prompt,
                user=rendered_input,
                max_tokens=config.MAX_TARGET_TOKENS,
                temperature=config.TEMPERATURE_TARGET,
            )
            target_response = tr.text
            target_finish = tr.finish_reason
            target_prompt_tokens = tr.prompt_tokens
            target_completion_tokens = tr.completion_tokens
            cost_usd += estimate_cost(target_model, tr.prompt_tokens, tr.completion_tokens)

            # 3) output-side judge (if applicable)
            if placement == "output":
                jp = render_judge_prompt(judge.id, "output", rule.system_prompt,
                                         rendered_input, target_response)
                jr = await client.chat_with_retry(
                    model=config.JUDGE_MODEL,
                    system=None,
                    user=jp,
                    max_tokens=config.MAX_JUDGE_TOKENS,
                    temperature=config.TEMPERATURE_JUDGE,
                )
                judge_out_text = jr.text
                judge_out_verdict = parse_verdict(jr.text)
                judge_prompt_tokens += jr.prompt_tokens
                judge_completion_tokens += jr.completion_tokens
                cost_usd += estimate_cost(config.JUDGE_MODEL, jr.prompt_tokens, jr.completion_tokens)
                if judge_out_verdict == "BLOCK":
                    final_action = "blocked_output"

            # 4) violation detection only if response was delivered
            if final_action == "delivered":
                rule_violated = rule.detect_violation(target_response or "")
    except Exception as e:
        err = f"{type(e).__name__}: {e}"

    latency = time.perf_counter() - t0
    return TrialResult(
        attack_id=attack.id,
        attack_category=attack.category,
        attack_source=attack.source,
        rule_id=rule.id,
        judge_variant=judge.id,
        judge_placement=placement,
        target_model=target_model,
        judge_model=config.JUDGE_MODEL,
        rendered_input=rendered_input,
        target_response=target_response,
        target_finish_reason=target_finish,
        judge_input_text=judge_in_text,
        judge_input_verdict=judge_in_verdict,
        judge_output_text=judge_out_text,
        judge_output_verdict=judge_out_verdict,
        final_action=final_action,
        rule_violated=rule_violated,
        cost_usd=cost_usd,
        latency_s=latency,
        target_prompt_tokens=target_prompt_tokens,
        target_completion_tokens=target_completion_tokens,
        judge_prompt_tokens=judge_prompt_tokens,
        judge_completion_tokens=judge_completion_tokens,
        error=err,
    )


async def run_all(plans: List[Plan], concurrency: int,
                  target_model: str = config.TARGET_MODEL,
                  on_progress=None,
                  cost_cap_usd: float = config.COST_CAP_USD) -> List[TrialResult]:
    sem = asyncio.Semaphore(concurrency)
    client = OpenRouterClient()
    results: List[TrialResult] = []
    total_cost = [0.0]
    aborted = [False]
    lock = asyncio.Lock()

    async def _wrapped(plan: Plan, idx: int):
        if aborted[0]:
            return
        async with sem:
            r = await _run_one(client, plan, target_model)
            async with lock:
                results.append(r)
                total_cost[0] += r.cost_usd
                if on_progress:
                    on_progress(len(results), len(plans), total_cost[0], r)
                if total_cost[0] >= cost_cap_usd and not aborted[0]:
                    aborted[0] = True
                    print(f"\n!! cost cap ${cost_cap_usd:.2f} reached, halting further trials")

    tasks = [asyncio.create_task(_wrapped(p, i)) for i, p in enumerate(plans)]
    await asyncio.gather(*tasks, return_exceptions=False)
    return results


def write_run(results: List[TrialResult], out_path: Path,
              meta: Dict[str, Any]) -> None:
    payload = {
        "meta": meta,
        "results": [asdict(r) for r in results],
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
