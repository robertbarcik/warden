# Warden — Repo Conventions

## What this is

A small evaluation framework that tests whether an LLM-as-judge can intercept
public jailbreak attacks before they breach four representative deployment
rules (secret extraction, persona, topic, mock tool boundary).

Inspired by ZetaLib (https://github.com/Exocija/ZetaLib). See `DANGER.md`
for the safety notice that applies to all attack content.

## Layout

- `src/warden/` — Python package: client, orchestrator, scoring, reporting
- `data/attacks/` — adversarial test inputs (YAML, safety-wrapped). **Read DANGER.md.**
- `data/omniguard.txt` — mirrored guardrail prompt from ZetaLib (used as one judge variant)
- `results/` — JSON outputs from `warden run`, plus generated `report.html`
- `booklet/` — Token-Economics-style HTML booklet with theory + results + defense playbook

## Commands

```bash
source .venv/bin/activate
warden run            # runs full sweep (~560 trials, ~5–10 min, ~$1)
warden run --attacks zetalib_dan6_grok --rules R1 --judges J0 --target deepseek/deepseek-chat-v3.1
warden report results/run-YYYYMMDD-HHMMSS.json   # generates HTML
warden stats results/run-YYYYMMDD-HHMMSS.json    # quick CLI summary
python booklet/_src/tools/build_html.py          # builds booklet/index.html
```

## Models (OpenRouter, open-source only)

- Target: `deepseek/deepseek-chat-v3.1`
- Judge:  `qwen/qwen3-235b-a22b`

Do not switch to vendor models (Claude, GPT, Gemini) — they have API moderation
that may reject the adversarial inputs and risk account flags.

## Distinctness from sibling repos

- **bloom** does multi-turn iterative red-teaming (evaluator and target alternate).
  Warden is **single-turn**: each attack is one prompt, the target replies once,
  the judge decides. Do not port bloom's `ConversationOrchestrator` here.
- **selfjudge** measures models judging their own outputs. Warden uses one model
  as target and a different model as judge.
- **geobias** is the closest stylistic sibling for the HTML report.

## Code reuse provenance

- Concurrency pattern: `bloom/src/bloom/stages/step3_rollout.py:285-361`
- HTML report style: `geobias/src/geobias/templates/report.html`
- Booklet build: `barcik-training-publications/_sources/token-economics/tools/build_html.py`

## Safety conventions (non-negotiable)

1. Every attack YAML must contain `is_test_input: true` and the
   `[BEGIN ADVERSARIAL TEST INPUT — DO NOT EXECUTE]` / `[END ...]` payload wrap.
2. The HTML report renders attack payloads inside `<details>` (collapsed by default).
3. The booklet describes attacks abstractly; full payloads stay in `data/attacks/` only.
4. `DANGER.md` and `data/attacks/README.md` must remain in place.
