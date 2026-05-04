"""warden CLI — `warden run` and `warden stats`.

The HTML report is no longer produced as a standalone artifact; the booklet
under `booklet/index.html` is now the single output. Build the booklet with
`python booklet/_src/tools/build_html.py`.
"""
from __future__ import annotations
import asyncio
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

import click

from . import config
from .attacks import load_all as load_all_attacks, load_by_ids
from .rules import RULES
from .judges import VARIANTS as JUDGE_VARIANTS
from .orchestrator import build_plans, run_all, write_run, TrialResult


def _parse_csv(s: Optional[str]) -> Optional[List[str]]:
    if s is None or s == "":
        return None
    return [x.strip() for x in s.split(",") if x.strip()]


@click.group()
def cli() -> None:
    """warden — testing LLM-as-judge defenses against public jailbreaks."""


def _model_slug(model_id: str) -> str:
    """Compress 'vendor/model-name' into a filesystem-friendly slug."""
    return model_id.replace("/", "-").replace(".", "")


@cli.command("run")
@click.option("--attacks", "attacks_csv", type=str, default=None,
              help="Comma-separated attack IDs (default: all)")
@click.option("--rules", "rules_csv", type=str, default=None,
              help="Comma-separated rule IDs (default: all)")
@click.option("--judges", "judges_csv", type=str, default=None,
              help="Comma-separated judge variants (default: J0,J1,J2,J3)")
@click.option("--target", "target_model", type=str, default=config.TARGET_MODEL,
              help="OpenRouter target model ID (default: %s)" % config.TARGET_MODEL)
@click.option("--concurrency", type=int, default=config.CONCURRENCY)
@click.option("--cost-cap", type=float, default=config.COST_CAP_USD,
              help="Abort run if total spend exceeds this many USD")
@click.option("--out", "out_path", type=click.Path(path_type=Path), default=None)
def run_cmd(attacks_csv, rules_csv, judges_csv, target_model, concurrency, cost_cap, out_path):
    """Run the full attack × rule × judge sweep."""
    # Resolve selections
    if attacks_csv:
        atks = load_by_ids(_parse_csv(attacks_csv))
    else:
        atks = load_all_attacks()
    rule_ids = _parse_csv(rules_csv) or list(RULES.keys())
    rules = [RULES[r] for r in rule_ids]
    judge_ids = _parse_csv(judges_csv) or list(JUDGE_VARIANTS.keys())
    judges = [JUDGE_VARIANTS[j] for j in judge_ids]

    if target_model not in config.PRICING:
        click.echo(f"WARNING: {target_model} not in PRICING table; cost estimate will be 0")

    plans = build_plans(atks, rules, judges)
    click.echo(f"Plans: {len(plans)} trials  "
               f"[{len(atks)} attacks × {len(rules)} rules × "
               f"{sum(2 if j.has_judge else 1 for j in judges)} conditions]")
    click.echo(f"Target: {target_model}")
    click.echo(f"Judge:  {config.JUDGE_MODEL}")
    click.echo(f"Concurrency: {concurrency}, cost cap: ${cost_cap:.2f}")

    started = time.time()
    last_print = [0.0]
    def _progress(done, total, cost, last):
        if time.time() - last_print[0] < 1.5 and done != total:
            return
        last_print[0] = time.time()
        click.echo(f"  {done}/{total}  ${cost:.4f}  "
                   f"{last.attack_id[:24]}/{last.rule_id}/{last.judge_variant}-{last.judge_placement[:3]}")

    results = asyncio.run(run_all(plans, concurrency=concurrency,
                                  target_model=target_model,
                                  on_progress=_progress, cost_cap_usd=cost_cap))
    elapsed = time.time() - started

    ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    out_path = out_path or (config.RESULTS_DIR / f"run-{ts}-{_model_slug(target_model)}.json")
    meta = {
        "ts_utc": datetime.now(timezone.utc).isoformat(),
        "target_model": target_model,
        "judge_model": config.JUDGE_MODEL,
        "concurrency": concurrency,
        "cost_cap_usd": cost_cap,
        "elapsed_s": elapsed,
        "n_attacks": len(atks),
        "n_rules": len(rules),
        "n_judges": len(judges),
        "n_trials": len(results),
        "total_cost_usd": sum(r.cost_usd for r in results),
        "n_errors": sum(1 for r in results if r.error),
    }
    write_run(results, out_path, meta)
    click.echo(f"\nWrote {out_path}")
    click.echo(f"Cost: ${meta['total_cost_usd']:.4f}   Elapsed: {elapsed:.1f}s   "
               f"Errors: {meta['n_errors']}")


@cli.command("stats")
@click.argument("run_path", type=click.Path(exists=True, path_type=Path))
def stats_cmd(run_path):
    """Print a per-rule per-condition summary table to the terminal."""
    data = json.loads(run_path.read_text())
    results = data["results"]
    meta = data["meta"]
    click.echo(f"\n{run_path.name}   target={meta['target_model']}   judge={meta['judge_model']}")
    click.echo(f"  trials={len(results)}   cost=${meta['total_cost_usd']:.4f}   "
               f"errors={meta['n_errors']}   elapsed={meta['elapsed_s']:.1f}s\n")

    # Aggregate ASR by rule × condition
    from collections import defaultdict
    by_cell = defaultdict(lambda: {"n": 0, "viol": 0, "blocked": 0, "err": 0})
    for r in results:
        cond = f"{r['judge_variant']}-{r['judge_placement']}"
        cell = by_cell[(r["rule_id"], cond)]
        cell["n"] += 1
        if r.get("error"):
            cell["err"] += 1
            continue
        if r["final_action"].startswith("blocked"):
            cell["blocked"] += 1
        if r["rule_violated"]:
            cell["viol"] += 1

    rules = sorted({r["rule_id"] for r in results})
    conds = sorted({f"{r['judge_variant']}-{r['judge_placement']}" for r in results})
    # Header
    click.echo(f"  {'condition':<14}  " + "  ".join(f"{r:>14}" for r in rules))
    for cond in conds:
        cells = []
        for rid in rules:
            cell = by_cell.get((rid, cond), {"n": 0, "viol": 0, "blocked": 0, "err": 0})
            n = cell["n"]
            asr = (cell["viol"] / n * 100.0) if n else 0.0
            blocked = cell["blocked"]
            cells.append(f"ASR {asr:5.1f}% B={blocked:>2}")
        click.echo(f"  {cond:<14}  " + "  ".join(f"{c:>14}" for c in cells))


if __name__ == "__main__":
    cli()
