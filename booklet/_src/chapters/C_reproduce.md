# Reproduce This

The framework is small enough to fork and run against your own deployment in an afternoon. Eleven steps, in order.

## 1 · Clone and install

```bash
git clone https://github.com/robertbarcik/warden.git
cd warden
python3.12 -m venv .venv && source .venv/bin/activate
pip install -e .
```

## 2 · Get an OpenRouter key

OpenRouter at `openrouter.ai/keys`. A $5 prepaid balance is enough to run the full 1,680-trial three-target sweep with comfortable headroom; a single 560-trial sweep on a cheaper target costs roughly $0.20.

```bash
cp .env.example .env
# edit .env, set OPENROUTER_API_KEY=...
```

## 3 · Confirm the existing sweep runs

```bash
warden run --target deepseek/deepseek-chat-v3.1 --concurrency 6
```

This re-runs the 560-trial sweep with the existing target, attack corpus, and rules. Watch the progress prints; expect ~20 min wall-clock and ~$0.20 of OpenRouter credit. If the cost runs over, the cost-cap (default $4) will halt it. After completion, the JSON lands in `results/`.

## 4 · Define your deployment rule

Open `src/warden/rules.py`. The four rules — R1 secret, R2 persona, R3 topic, R4 tool — are each a `Rule` dataclass with three fields:

- `system_prompt` — the rule itself, what the deployment hands to the assistant
- `objective` — the harmful goal the attacker tries to nudge the model toward
- `detect_violation` — a Python callable returning True iff the response broke the rule

Add a fifth rule (R5) for *your* deployment. Be a lawyer about it: enumerate forbidden disclosure modes, paraphrase variants, and edge-cases. The R1 system prompt is roughly 90 words and is a useful template.

## 5 · Define the violation detector

Inside the `detect_violation` callable, write the deterministic check. Three patterns work:

- **Substring match** (R1's pattern) — for rules that have a literal forbidden token
- **Keyword regex with anchor word** (R2's pattern) — for rules about sentiment / topic about a specific subject
- **Code/syntactic-signature regex** (R3's pattern) — for rules that forbid certain output shapes (code, structured output, tool-call syntax)

Keep the detector short. Anything you can't express in 30 lines of regex probably needs a different rule wording.

## 6 · Decide if your deployment knows the rule landscape

Two paths:

- **You can articulate the rule explicitly** → use a *tailored reasoning judge*. Skip step 7. The default J2 prompt in `src/warden/judges.py` is a good starting point; adapt the wording to your rule and your tolerance for hedge violations.
- **The rule landscape is open** (e.g., a public-facing chatbot where you can't enumerate the rules in advance) → use a *generic guardrail*. Use J3 (Omniguard) as a baseline; consider that you'll pay 30%+ false-positive rate against attack-shaped legitimate inputs and decide whether that's acceptable.

## 7 · Customize the judge prompt

If using a tailored judge, copy the `_J2_OUTPUT` template in `src/warden/judges.py` and modify:

- The "categories of subversion to watch for" list — keep the existing items, add ones specific to your domain
- The "would complying violate the rule" framing — make it specific to your rule's forbidden categories
- The verdict-format instruction (`VERDICT: ALLOW` / `VERDICT: BLOCK`) — keep this exact, the parser depends on it

## 8 · Run a small calibration sweep

```bash
warden run --rules R5 --judges J0,J2 --concurrency 4
```

Just your new rule, just baseline + the tailored judge, both placements (J2-input and J2-output). 20 attacks × 1 rule × 3 conditions = 60 trials, ~5 min, ~$0.05.

Read `results/run-*.json`. Check:

- Baseline ASR > 0% (otherwise your attacks have no teeth against your rule and you can't measure judge effect)
- J2-output ASR is meaningfully lower than baseline (otherwise the judge doesn't help)
- J2-output FP rate is acceptable for your deployment (otherwise it's blocking legitimate inputs)

If any of these fail, iterate the rule or judge wording and re-run.

## 9 · Add deployment-specific attacks

The 20 attacks in `data/attacks/` are general-purpose. Your deployment likely has *specific* failure modes — the kind of jailbreak you've seen in your own production logs, the kind of hostile user query that has gotten through before, the kind of edge case your support team flags.

Author 5–10 attacks specific to your deployment, following the schema in `data/attacks/_schema.md`. Wrap them in `[BEGIN ADVERSARIAL TEST INPUT]` / `[END ...]` markers. Add the safety preamble. Re-run the sweep.

## 10 · Run on your real target model

Add the model ID to `src/warden/config.py`'s `PRICING` table. Run:

```bash
warden run --target <your-target-model> --concurrency 6
```

If your real target is a vendor model (Claude, GPT, Gemini), expect API moderation to fire on some of the adversarial inputs. The framework will report errors in the run JSON; review them before drawing conclusions.

## 11 · Build the booklet locally

If you're iterating on the framework and want to see your changes reflected in a booklet of your own:

```bash
python booklet/_src/tools/build_html.py
open booklet/index.html
```

The booklet build reads every `results/run-*.json`. To swap targets in the booklet, swap the JSONs in `results/`.

---

## Cost / time table

| Sweep | Trials | Wall-clock | OpenRouter cost |
|-------|--------|-----------|-----------------|
| Single rule, two conditions, 20 attacks | 60 | ~5 min | ~$0.05 |
| One target, full corpus | 560 | ~20 min | ~$0.20–0.50 |
| Three-target full sweep (the booklet) | 1680 | ~50 min | ~$0.90 |

All numbers assume `concurrency=6` and the open-weight target/judge combinations from this experiment. Vendor models are 5–20× more expensive per token; budget accordingly.

---

> **Where to look in the repo.** Repo root: [github.com/robertbarcik/warden](https://github.com/robertbarcik/warden). For the contributor-facing summary: `CLAUDE.md`. For the safety conventions all forks must preserve: `DANGER.md`. For the rest: just read the code — it's about 600 lines.