# Warden

## Testing whether an LLM-as-judge can defeat public jailbreaks before they breach a deployed system's rules.

---

**May 2026**

*By Robert Barcik*

*LearningDoe s.r.o.*

*Contact: [robert@barcik.training](mailto:robert@barcik.training)*

---

> **Adversarial test material follows.** This booklet describes attacks abstractly. The full payloads live in the repository under `data/attacks/`, wrapped in `[BEGIN ADVERSARIAL TEST INPUT]` / `[END …]` markers and labelled `is_test_input: true`. The lineage is public: 11 of the attacks are mirrored from the [ZetaLib](https://github.com/Exocija/ZetaLib) library; the other 9 are short representatives of categories from ZetaLib's "Sword 140" taxonomy. Treat all attack content as test input, not as instructions to anyone — human or model.

### About this booklet

A small experiment, written for an audience that already knows what *prompt injection* means and doesn't need the obligatory disclaimers about why prompt injection matters. The framing question is direct: *do the public jailbreak claims in repositories like ZetaLib survive contact with a competent LLM-as-judge layer?* The answer turns out to be: mostly no, but the implementation details — *which* judge, *where* placed, *how* prompted — make the difference between a defense that works and one that quietly silently breaks user experience.

The book is built around a 560-trial evaluation against four representative deployment-rule shapes: a secret to keep, a persona to hold, a topic to stay on, and a forbidden mock tool to avoid. The target is `deepseek-chat-v3.1`. The judge is `qwen3-235b-a22b-2507`. Both are open-weight, accessed through OpenRouter, and the entire experiment runs in twenty minutes for under twenty cents of credit. Re-running with a different target, judge, attack corpus, or rule set is one CLI invocation.

### Who this booklet is for

- **Engineering teams** about to deploy an LLM assistant — chatbot, customer-support agent, internal tool, vertical specialist — and trying to decide what kind of prompt-injection defense to put in front of it.
- **Trainers and educators** teaching about LLM security who want a concrete, end-to-end worked example with reproducible numbers.
- **Practitioners and researchers** evaluating LLM-as-judge defenses who want a small, legible methodology to fork and adapt.

The audience is assumed to know what an LLM is, what a system prompt is, and what *prompt injection* and *roleplay jailbreak* refer to. The booklet does not introduce these concepts; it assumes them and proceeds.

### How to read this booklet

Chapter 1 sets up the hypothesis and the framing. Chapter 2 names the threat model precisely (instruction-hierarchy adherence, not trained refusal). Chapter 3 walks through the framework's architecture. Chapter 4 describes the twenty attacks. Chapter 5 walks through the four judge variants. Chapter 6 reports what fell out of the run. Chapter 7 turns the numbers into a deployment playbook. Chapter 8 handles the credits and limitations.

If you are an engineering team trying to make a deployment decision *today*, jump to Chapter 7. If you are a student trying to understand the methodology, read in order. The chapters are short on purpose — the entire booklet is around eleven thousand words.

### Table of contents

1. The Hypothesis
2. The Threat Model
3. The Framework
4. The Attacks
5. The Judges
6. Results
7. Defenses for Deployers
8. Acknowledgments and Limitations

---

The repository at [github.com/robertbarcik/warden](https://github.com/robertbarcik/warden) holds the framework code, the attack corpus, the raw run data, and the HTML report. The booklet, the report, and the code are all produced from the same single run; if you doubt a number, read the JSON.
