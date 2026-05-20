# Acknowledgments and Limitations

## Inspiration

This work was triggered by a student sharing a link to [ZetaLib](https://github.com/Exocija/ZetaLib) — a library cataloguing both attacks ("Sword 140") and defenses ("Shield 50") against LLMs. The organizing premise — *put the offence and the defence in the same repository, treat them as halves of the same craft* — is what made it the right artefact to test. A library that publishes both invites someone to run the experiment. Warden is that experiment, on a deliberately small scale. Eleven of the twenty attacks mirror ZetaLib's payloads (with safety wrappers); Omniguard is one of the four judge variants. Without ZetaLib, this booklet would either not exist or be a worse version of itself.

## Limitations

A short and honest list of where the conclusions do not generalize.

**Single-turn only.** The framework does not measure multi-turn attack adaptation, where an attacker LLM iterates against the target's refusals to find one that works. Multi-turn red-teaming is a real and harder problem and is the subject of frameworks like [bloom-evals](https://github.com/safety-research/bloom-evals). The single-turn case tested here is the more common deployment scenario but not the worst case.

**Indirect / RAG-borne prompt injection out of scope.** Where the attack arrives inside a retrieved document instead of a user message, the attack surface is different. Warden does not test this case. Mitigations partially overlap (an output-side judge helps) but the experiment does not measure the overlap.

**Trained-refusal categories not tested.** The four rules in this experiment are instruction-hierarchy rules — system-prompt-defined. They do not include trained-refusal categories like weapons synthesis, child safety, or self-harm. Frontier models are evaluated against those by their developers using different methodology. We are explicit about not testing the same thing.

**Static attacks, not attacks tuned to the judge.** All twenty attacks were authored or selected without sight of the judge prompts. An attacker who optimized specifically against the judges in this experiment would do better than these results suggest. The judges should be treated as one defensive layer — strong against off-the-shelf attacks, less strong against attacks tuned to their specific blind spots. Iterative attack-vs-judge — running an attacker loop that mutates successful attacks until the judge breaks — is one of the most useful follow-up experiments and the framework supports it.

**Time-bounded conclusions.** The viral attacks of 2026 are not the viral attacks of 2025. By 2027 the effective set of public jailbreaks will look meaningfully different. The framework is built to be re-run on a new corpus; the headline numbers in this booklet are point-in-time.

**Rule wording and detector wording are part of the result.** A baseline ASR is a property of *that wording* of the rule and *that wording* of the violation detector. The recommendation in [Chapter 8](#defenses-for-deployers) to "write the rule like a lawyer" is not optional methodological advice — it is part of the experimental setup, and any deployment trying to replicate the results must do the same work. (See the *honest interpretation* note in [Chapter 7](#results) for what this means concretely about the converging 1.2% J2-output ASR across targets.)

## Final word

The student who sent me the ZetaLib link did not believe his own claim that the library was "the only AI library you need." He sent it because it looked impressive and wanted to know what to make of it. The honest answer turns out to be: the attacks are real but mostly defeated by even modest judge layers, the good defensive technique published in the same library (Omniguard) is not always the best choice for a specific deployment, and the most important variables are not the judge model — they are whether you wrote your deployment rule like a lawyer, where you placed the judge in the pipeline, and whether you are honest about the noise floor in your measurement methodology.

Code, corpus, raw runs, and this booklet are at [github.com/robertbarcik/warden](https://github.com/robertbarcik/warden) — small enough to fork and adapt, which is the point.

> **Key takeaways**
> - The attack lineage is explicit: 11 of 20 attacks mirror ZetaLib's `Prompts/Jailbreaks/`, and Omniguard is one of the four judge variants. Without ZetaLib, this experiment would either not have happened or would be an inferior version of itself.
> - Every conclusion in this booklet is bounded by what was tested: three open-weight targets, one open-weight judge, twenty static attacks, four rules, single-turn only. The framework is small enough to fork and re-run with different choices — that is the productive output, not the specific numbers.
> - The numbers in this booklet are point-in-time. The viral attacks of 2026 are not the viral attacks of 2025; by 2027 the effective set will look different. Plan to re-run.

> **Discussion questions**
> 1. The most useful follow-up experiment named in the limitations is *iterative attack-vs-judge* — running an attacker loop that mutates the most successful attacks until the judge starts to leak. If you ran ten rounds of mutation against J2-output, where would you expect ASR to settle? What evidence would tell you the judge was actually defeated rather than just temporarily evaded?
> 2. The "rule wording is part of the result" point cuts in two directions. Sketch one rule wording that would make this booklet's headline ASR look *worse* than it does, and one that would make it look *better*. What does that tell you about how to read any single jailbreak benchmark?
