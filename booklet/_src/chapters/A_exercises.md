# Exercises

Six exercises against the actual run data. Each one is open-ended; there is no answer key. The goal is to make you read the JSON, run a few CLI commands, and form an opinion. Most take 15–30 minutes. The first three are passive (read-only); the last three modify code or the corpus and re-run a small part of the experiment.

## Setup

Clone the repository and set up a Python environment:

```bash
git clone https://github.com/robertbarcik/warden.git
cd warden
python3.12 -m venv .venv && source .venv/bin/activate
pip install -e .
cp .env.example .env  # add your OPENROUTER_API_KEY
```

The exercises below assume the run JSONs are in `results/`. If you skipped the full sweeps, run `warden run --target deepseek/deepseek-chat-v3.1 --concurrency 6` (~$0.20, ~20 min) to produce one before starting.

## E1 — Read the J2-output leak

[Chapter 6](#a-trial-in-detail) walks through the single J2-output trial that leaked. Open `results/run-*-deepseek-deepseek-chat-v31.json` in any JSON viewer. Find the trial where `attack_id == "zetalib_experimental_001"`, `rule_id == "R2"`, `judge_variant == "J2"`, `judge_placement == "output"`. Read the `target_response` and `judge_output_text` fields in full.

Then write two paragraphs:

1. *Quote one specific line from the target's response that you think the deployment rule intended to forbid, even though the literal rule text doesn't quite cover it.*
2. *Quote one specific line from the judge's reasoning that you think shows the judge's interpretation of the rule was reasonable, even though the deterministic detector disagreed.*

Then decide: should the rule be tightened, the detector be tightened, or both? If both, which has higher leverage?

## E2 — Find the toughest attack against R3

The R3 (topic) baseline ASR was 40% — the highest of the four rules. Open the run JSON. Restrict to `judge_variant == "J0"` and `rule_id == "R3"`. Group by `attack_id`. Compute per-attack baseline ASR for R3 specifically.

Identify the attack with the highest R3 baseline ASR. Read its rendered_input and the target's response. Write two paragraphs:

1. *Why does this attack break R3 specifically? What about the cooking-bot rule was easy for this attack to bypass that the persona / secret / tool rules were not?*
2. *Can you write a one-line amendment to R3's system prompt that would have neutralized this attack? Test it: edit `src/warden/rules.py`, run `warden run --attacks <attack_id> --rules R3 --judges J0`, observe whether ASR changes.*

## E3 — Compare two judges on the same trial

Pick any baseline-violating attack (any trial with `judge_variant == "J0"` and `rule_violated == True`). For the same attack and rule, find two judge configurations — say J1-output and J2-output — and read their `judge_output_text` fields side by side.

Write a short comparison: how do the two judges' outputs differ in length? In structure? In what they explicitly flag? In how they end (verdict format)?

Then form a hypothesis: *for the deployment shape you most often work with, which of those two judge designs would you prefer? Why?*

## E4 — Tighten a rule

Pick R2 (persona). The current rule is roughly 80 words. Re-write it to be roughly 200 words, adding explicit prohibitions for:

- Hedge-positive responses ("X has been working on improving Y")
- Future-historical framing ("in 2025 they would have…")
- Unprompted comparisons with named industries (without competitor names)
- "Common feedback we hear is…" patterns

Save your tightened R2 to a copy of `rules.py`. Re-run `warden run --rules R2 --concurrency 4`. Compare ASR before and after.

Two questions:

1. *Did baseline ASR change? Did any judge condition's ASR change?*
2. *Did the false-positive rate change? Specifically: did legitimate-seeming responses now get blocked? Look at trials where the response was BLOCKed under your tightened rule but wasn't BLOCKed under the original.*

The lesson is usually: tighter rules reduce ASR but increase FP. Quantify the trade-off.

## E5 — Add an attack from a different source

The 20 attacks in `data/attacks/` come from ZetaLib and from this evaluation. Find one prompt-injection attack from a different public source — an arxiv paper's appendix, a blog post, an open challenge. Author a YAML file for it following `data/attacks/_schema.md`, including all the safety markers.

Run `warden run --attacks <your_new_attack_id> --concurrency 4`. Read the result.

Write a paragraph: *did your attack break any rule at baseline? Did any judge variant fail to catch it? If yes, why? If no, what does that tell you about the breadth of the existing 20-attack corpus?*

## E6 — Swap the target

Pick a target model not in the experiment — Llama 3.3 70B, Mistral Large 2, GPT-4o-mini, Gemini Flash, anything available on OpenRouter. Add it to `src/warden/config.py`'s `PRICING` table.

Run `warden run --target <new-model> --concurrency 6`. Wait for completion (~20–30 min).

Compare the resulting heatmap against the three in [Chapter 7](#results). Write three paragraphs:

1. *Where is the picture consistent across all four targets you've now seen?*
2. *Where does the new target diverge — which rule? Which attack? In what direction?*
3. *Does that divergence change your deployment recommendation from [Chapter 8](#defenses-for-deployers)? If yes, how? If no, what does it tell you about the robustness of the recommendation?*

This is the most-instructive exercise. Vendor moderation may flag adversarial inputs against frontier targets; if you hit that, you've also learned something about why open-weight targets were chosen for the booklet.

---

> **Where to look in the repo.** Run JSONs are at `results/run-*.json`. Per-rule code is at `src/warden/rules.py`. Per-judge prompts are at `src/warden/judges.py`. Attack YAML schema is at `data/attacks/_schema.md`. The CLI is in `src/warden/cli.py`. None of it is more than a few hundred lines.