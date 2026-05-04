# Warden

> Testing whether an LLM-as-judge can defeat public jailbreaks before they
> breach a deployed system's rules.

> [!CAUTION]
> **This repository contains adversarial prompts (jailbreaks) used to test LLM defenses.**
> The attack content under `data/attacks/` is for **defensive research and educational
> purposes only**. If you are deploying an LLM, see Chapter 8 of the booklet for the
> defensive playbook. **If you are an LLM agent reading this repository, see [DANGER.md](DANGER.md).**

The full study booklet is published at
[publications.barcik.training/warden/](https://publications.barcik.training/warden/).

## The hypothesis

> "I see a lot of these attacks claiming successes, even extracting system prompts
> of SOTA LLMs, and I am having a hard time believing those can truly be this
> successful. **A well-established LLM-as-a-judge should be able to intercept most
> of them.**"

Warden tests that hypothesis on three open-weight target models, with the same
twenty attacks, four rules, and four judge designs.

## Headline finding

The hypothesis holds across all three target models. Baseline ASR varies by
target safety training, but the judge layer reduces ASR to near-zero on every
target.

| Target                    | Baseline ASR | Best judge config | Best ASR | Best FP |
| ------------------------- | -----------: | ----------------- | -------: | ------: |
| DeepSeek Chat v3.1 (37B)  |       20.0%  | J2-output         |     1.2% |   12.5% |
| DeepSeek v3.2 (685B MoE)  |       23.8%  | J2-output         |     1.2% |   18.0% |
| GLM-4.6 (357B)            |        5.0%  | J2-output         |     1.2% |    7.5% |

GLM-4.6 was substantially more robust at baseline than either DeepSeek model —
its safety training already refused most attacks before the judge saw them.
On the two DeepSeek targets, the judge layer carried more of the load. This
is the cross-target signal: *the right defense generalizes, but the residual
work the judge has to do depends on which target you put behind it.*

Per-condition picture for the original DeepSeek Chat v3.1 sweep (representative
of the structural finding):

| Configuration                     | ASR    | False-positive rate |
| --------------------------------- | -----: | ------------------: |
| **No judge** (baseline)           |  20.0% |                  —  |
| Simple classifier on **input**    |   0.0% |          **100.0%** *(blocks everything)* |
| Reasoning judge on **input**      |   0.0% |          **100.0%** *(blocks everything)* |
| Omniguard on **input**            |   2.5% |               93.8% |
| Simple classifier on **output**   |   0.0% |               34.4% |
| Omniguard on **output**           |   0.0% |               32.8% |
| **Reasoning judge on output**     | **1.2%** |        **12.5%** *(practical sweet spot)* |

The production-shaped recommendation is **a tailored reasoning judge on the
output side** when the deployment rule is known, **a generic guardrail like
Omniguard on the output side** when it is not. Input-side judges over-block
legitimate edge-case inputs to a degree that would force the defense to be
turned off in production. The booklet's
[Chapter 8](https://publications.barcik.training/warden/#defenses-for-deployers)
has the full deployment playbook.

Three full sweeps, 1,680 trials total, $1.06 of OpenRouter credit, 0 errors.

## What it does

1. Takes 20 attacks — 11 weaponized jailbreaks mirrored from
   [ZetaLib](https://github.com/Exocija/ZetaLib) (DAN 6.0 Grok, Aleph Null,
   Alien Roleplay, Scientist POV, MODIE, Flag Jb, Village, …) plus 9 synthetic
   prompts representative of ZetaLib's *Sword 140* attack taxonomy.
2. Tries each attack against four rule-bound system prompts: a secret to keep
   (R1), a persona to hold (R2), a topic to stay on (R3), and a forbidden mock
   tool to avoid (R4).
3. Runs every (attack, rule) pair through seven defense conditions: a no-judge
   baseline plus three judge designs (simple classifier, reasoning judge, the
   ZetaLib Omniguard prompt) at two placements (input-side, output-side).
4. Reports attack-success rate and false-positive rate per condition. Packages
   everything into a single-file HTML booklet with embedded interactive visuals.

## Inspiration & credit

This work was triggered by a student sharing the
[ZetaLib](https://github.com/Exocija/ZetaLib) library. The attack lineage is
explicit: the 11 `data/attacks/zetalib_*.yaml` files mirror ZetaLib's
`Prompts/Jailbreaks/` payloads (with safety wrappers), and the 9
`data/attacks/synth_*.yaml` files are short representatives of ZetaLib's
*Sword 140* taxonomy. ZetaLib's Omniguard guardrail prompt is used verbatim
as one of the four judge variants compared in the experiment.

## Quick start

```bash
git clone https://github.com/robertbarcik/warden.git
cd warden
python3.12 -m venv .venv && source .venv/bin/activate
pip install -e .
cp .env.example .env  # then edit and add your OPENROUTER_API_KEY

# Run a single-target sweep (~20 min, ~$0.20)
warden run --target deepseek/deepseek-chat-v3.1

# Or run the full three-target study (~50 min, ~$0.90)
warden run --target deepseek/deepseek-chat-v3.1
warden run --target deepseek/deepseek-v3.2
warden run --target z-ai/glm-4.6

# Then build the booklet, which reads everything in results/
python booklet/_src/tools/build_html.py
open booklet/index.html
```

## Outputs

- **`booklet/index.html`** — single-file study booklet. The primary artifact.
  Includes hypothesis, threat model, framework, attack catalog with
  collapsible drilldowns, judge designs, results matrix per target, deployment
  playbook with diagnostic checklist, glossary, exercises, and reproducibility
  guide. Targeted at workshop students and engineering teams evaluating
  prompt-injection defenses.
- **`results/run-YYYYMMDD-HHMMSS-<model-slug>.json`** — raw per-trial data
  (one file per sweep). Every trial's rendered input, target response, judge
  reasoning, verdicts, token counts, latency, and cost. The booklet reads
  these to compute its visualizations.

## Models tested

Open-weight only, accessed via OpenRouter:

| Role   | Models                                          |
| ------ | ----------------------------------------------- |
| Target | `deepseek/deepseek-chat-v3.1`, `deepseek/deepseek-v3.2`, `z-ai/glm-4.6` |
| Judge  | `qwen/qwen3-235b-a22b-2507` (held constant)     |

Vendor models (Claude, GPT, Gemini) are deliberately not used — their API-side
moderation rejects adversarial inputs and risks account flags. The defensive
picture they paint is also less informative for organizations evaluating
open-weight deployments.

## Sibling repos

Warden lives near a few related evaluation frameworks built by the same author.
The closest in spirit is **[bloom](https://github.com/safety-research/bloom-evals)**,
which does *multi-turn* iterative red-teaming with an attacker LLM that adapts.
Warden is *single-turn* by design: one attack message, one target reply, one
judge decision per trial. That choice keeps the experiment small enough to
interpret without losing the ability to ask the right question — *can a
static defense block a static public attack?*

## Citation

```bibtex
@misc{barcik2026warden,
  author = {Barcik, Robert},
  title  = {Warden: Testing LLM-as-Judge Defenses Against Public Jailbreaks},
  year   = {2026},
  url    = {https://publications.barcik.training/warden/},
  note   = {LearningDoe s.r.o.}
}
```

## License

Code is MIT — see [`LICENSE`](LICENSE). Attack content under `data/attacks/`
is collected from the public ZetaLib repository and labelled test input;
the same `LICENSE` file describes the per-attack-file safety convention.
