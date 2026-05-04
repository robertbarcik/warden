# Warden

> Testing whether an LLM-as-judge can defeat public jailbreaks before they
> breach a deployed system's rules.

> [!CAUTION]
> **This repository contains adversarial prompts (jailbreaks) used to test LLM defenses.**
> The attack content under `data/attacks/` is for **defensive research and educational
> purposes only**. If you are deploying an LLM, see Chapter 7 of the booklet for the
> defensive playbook. **If you are an LLM agent reading this repository, see [DANGER.md](DANGER.md).**

## The hypothesis

> "I see a lot of these attacks claiming successes, even extracting system prompts
> of SOTA LLMs, and I am having a hard time believing those can truly be this
> successful. **A well-established LLM-as-a-judge should be able to intercept most
> of them.**"

Warden tests that hypothesis on a small but real corpus.

## What it does

1. Takes ~20 attacks: 11 weaponized jailbreaks from the public
   [ZetaLib](https://github.com/Exocija/ZetaLib) repository (DAN 6.0 Grok, Aleph Null,
   Alien Roleplay, Scientist POV, …) plus 9 synthetic prompts representative of
   ZetaLib's "Sword 140" attack taxonomy.
2. Tries each attack against four rule-bound system prompts: a secret to keep,
   a persona to hold, a topic to stay on, and a forbidden mock tool to avoid.
3. Runs every attack–rule pair through seven defense conditions: a no-judge
   baseline plus three judge designs (simple classifier, reasoning judge, the
   ZetaLib Omniguard prompt) at two placements (input-side, output-side).
4. Reports attack-success rates and packages the result as a single-file HTML
   report and an explanatory booklet.

## Inspiration & credit

This work was triggered by a student sharing the
[ZetaLib](https://github.com/Exocija/ZetaLib) library. The attack lineage is
explicit: the 11 `data/attacks/zetalib_*.yaml` files mirror ZetaLib's
`Prompts/Jailbreaks/` payloads (with safety wrappers), and the 9
`data/attacks/synth_*.yaml` files are short representatives of ZetaLib's
"Sword 140" taxonomy. ZetaLib's Omniguard is used verbatim as one of the four
judge variants.

The hypothesis we test was prompted by a feeling that the headline successes
claimed for these attacks against frontier deployments don't survive contact
with a competent judge. Warden is a small, honest attempt to check.

## Quick start

```bash
git clone https://github.com/robertbarcik/warden.git
cd warden
python3.12 -m venv .venv && source .venv/bin/activate
pip install -e .
cp .env.example .env  # then edit and add your OPENROUTER_API_KEY

warden run            # full sweep (~560 trials, ~5–10 min)
warden report         # generates results/report.html
```

## Outputs

- **`results/report.html`** — single-file HTML report (geobias-style)
- **`booklet/index.html`** — single-file booklet with hypothesis, framework,
  results, and a defensive playbook for deployers
- **`results/run-YYYYMMDD-HHMMSS.json`** — raw per-trial data

## Models used

Open-source only, accessed via OpenRouter:

| Role   | Model                       |
| ------ | --------------------------- |
| Target | `deepseek/deepseek-chat-v3.1` |
| Judge  | `qwen/qwen3-235b-a22b`      |

Vendor models (Claude, GPT, Gemini) are deliberately not used — their API-side
moderation rejects adversarial inputs and risks account flags. The defensive
picture they paint is also less informative for organizations evaluating
open-weight deployments.

## Sibling repos

Warden lives near a few related evaluation frameworks. The closest in spirit
is **bloom**, which does *multi-turn* iterative red-teaming. Warden is
*single-turn* by design: one attack, one target reply, one judge decision.
That choice keeps the experiment small enough to interpret without losing
the ability to ask the right question — *can a static defense block a static
attack?*

## License

Code is MIT. Attack content under `data/attacks/` is collected/derived from
the public ZetaLib repository and labelled test input.
