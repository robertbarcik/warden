# Acknowledgments and Limitations

## Inspiration

This work was triggered by a student sharing a link to [ZetaLib](https://github.com/Exocija/ZetaLib) — a popular library cataloguing both attacks ("Sword 140") and defenses ("Shield 50") against LLMs. ZetaLib's organizing premise — *put the offence and the defence in the same repository, name them in symmetric numbers, treat them as halves of the same craft* — is what made the library the right artefact to test. A library that publishes both Sword and Shield invites someone to run the experiment. Warden is that experiment, on a deliberately small scale.

The eleven `zetalib_*.yaml` attack files in `data/attacks/` mirror ZetaLib's `Prompts/Jailbreaks/` payloads with safety wrappers added. The Omniguard prompt under `data/omniguard.txt` is mirrored verbatim from ZetaLib's `Prompts/Guardrails/Omniguard/`. The nine `synth_*.yaml` files were authored for this evaluation, each as a representative of one *Sword 140* attack category not covered by the eleven weaponized payloads. Without ZetaLib, the experiment would either not have happened or would have been an inferior version of itself.

## Limitations

A short and honest list of where the conclusions do not generalize.

**One target model.** All trials run against `deepseek-chat-v3.1`. A different target — Qwen-3-235B, Llama-3.3-70B, GLM-4.6 — will produce different baseline ASRs and may interact with the judges differently. The experiment isolates *judge effect*, holding target constant. A wider study sweeps target × judge.

**One judge model.** All judge calls go to `qwen3-235b-a22b-2507`. A smaller, cheaper judge would let through attacks the larger judge catches; a different family (DeepSeek as judge against itself, GLM as judge against DeepSeek) would have different blind spots. The "use a reasoning judge on the output side" recommendation is structural; the specific FP-rate numbers depend on the model behind it.

**Single-turn only.** The framework does not measure multi-turn attack adaptation, where an attacker LLM iterates against the target's refusals to find one that works. Multi-turn red-teaming is a real and harder problem and is the subject of frameworks like [bloom-evals](https://github.com/safety-research/bloom-evals). The single-turn case tested here is the more common deployment scenario but not the worst case.

**Twenty attacks, not two hundred.** A larger corpus would average out per-attack noise but is unlikely to change the headline conclusion. The most impactful attacks at baseline (`synth_system_mimic`, `zetalib_aleph_null`, `synth_delimiter_injection`) are well-known mechanism families; a doubled corpus would mostly add additional examples of the same mechanisms.

**Static attacks.** All twenty attacks were authored or selected without sight of the judge prompts. An attacker who optimized specifically against the judges in this experiment would do better than these results suggest. The judges should be treated as one defensive layer — strong against off-the-shelf attacks, less strong against attacks tuned to their specific blind spots.

**Indirect / RAG-borne prompt injection out of scope.** Where the attack arrives inside a retrieved document instead of a user message, the attack surface is different. Warden does not test this case. Mitigations partially overlap (an output-side judge helps) but the experiment does not measure the overlap.

**Trained-refusal categories not tested.** The four rules in this experiment are instruction-hierarchy rules — system-prompt-defined. They do not include trained-refusal categories like weapons synthesis, child safety, or self-harm. Frontier models are evaluated against those by their developers using different methodology. We are explicit about not testing the same thing.

**Rule wording and detector wording are part of the result.** A 25% baseline ASR against R2 (persona) is a property of *that wording* of the persona rule and *that wording* of the violation detector. A weaker rule wording would produce higher ASR; a stronger one would produce lower. The recommendation in Chapter 8 to "write the rule like a lawyer" is not optional methodological advice — it is part of the experimental setup, and any deployment trying to replicate the results must do the same work.

**Only OpenRouter open-weight models tested.** Vendor models (Claude, GPT, Gemini) are not tested as targets. Their API-side moderation interferes with adversarial inputs in ways that would distort the experiment, and their evaluation methodology is the responsibility of their developers. The defensive picture for open-weight deployments — the more relevant picture for many production scenarios — is what Warden draws.

**Time-bounded conclusions.** The viral attacks of 2026 are not the viral attacks of 2025. By 2027 the effective set of public jailbreaks will look meaningfully different. The framework is built to be re-run on a new corpus; the headline numbers in this booklet are point-in-time.

## Future work

Three directions the framework supports without modification:

1. **Target sweeps.** Swap `TARGET_MODEL` in `src/warden/config.py` for any OpenRouter model and re-run. The same attack corpus, same judges, same rules; new numbers. A useful next move is comparing two or three open-weight targets of different sizes to see which rule-types are most sensitive to model capability.
2. **Judge-family ablation.** Swap `JUDGE_MODEL`. Same target, same attacks, same rules. The interesting question is whether judge-target family alignment (both DeepSeek, or both Qwen) hurts the judge's ability to recognize attacks the target would otherwise refuse — and whether *cross-family* judges catch more.
3. **Adversarial attack-vs-judge.** Run a small attacker-loop where each round mutates the most successful attacks and re-tests against the judge prompts. After ten rounds of mutation, where does ASR settle? This is not single-turn red-teaming the target; it is single-turn red-teaming the *judge*, which is a different and underexplored question.

Three more that need framework changes:

4. **Indirect / RAG-borne injection.** Add a "document corpus" alongside the attacks, where attacks live inside retrieved documents the target reads. Output-side judges should help; input-side judges have nothing to bite on.
5. **Multi-turn defense ablation.** Pair Warden's judge with bloom's multi-turn attacker. Does the static judge survive iterative adaptation? At what number of turns does it start to leak?
6. **Real-traffic FP measurement.** Replay anonymized production user messages through the judge in shadow mode and measure the false-positive rate against legitimate traffic, not against the synthetic FP-proxy this experiment uses.

## Repository

[github.com/robertbarcik/warden](https://github.com/robertbarcik/warden) — code, attack corpus, raw run JSON, HTML report, and this booklet. Re-running the experiment is `warden run`. Re-generating the report is `warden report`. Re-building the booklet is `python booklet/_src/tools/build_html.py`. The repository is small enough to fork and adapt; that is the point.

## Final word

The student who sent me the ZetaLib link did not believe his own claim that the library was "the only AI library you need." He sent it because it looked impressive and he wanted to know what to make of it. The honest answer turns out to be: the attacks are real but mostly defeated by even modest judge layers, the *good* defensive technique published in the same library (Omniguard) is not always the best choice for a specific deployment, and the most important variable is not the judge model — it is whether you wrote your deployment rule like a lawyer and where you placed the judge in the pipeline.

That is a more useful answer than "the library is impressive" or "the attacks don't work." It is the answer this booklet exists to make available to anyone deploying an LLM in production this year.

> **Key takeaways**
> - The attack lineage is explicit: 11 of 20 attacks mirror ZetaLib's `Prompts/Jailbreaks/`, and Omniguard is one of the four judge variants. Without ZetaLib, this experiment would either not have happened or would be an inferior version of itself.
> - Every conclusion in this booklet is bounded by what was tested: three open-weight targets, one open-weight judge, twenty static attacks, four rules, single-turn only. The framework is small enough to fork and re-run with different choices — that is the productive output, not the specific numbers.
> - The numbers in this booklet are point-in-time. The viral attacks of 2026 are not the viral attacks of 2025; by 2027 the effective set will look different. Plan to re-run.

> **Discussion questions**
> 1. The "Future work" list includes adding indirect / RAG-borne prompt injection. What changes to the framework's data structures and judge prompts would be needed? Sketch the diff.
> 2. The booklet repeatedly notes that *open-weight* models are the focus and that vendor models are deliberately not tested. List two ways the picture might look different on a frontier vendor model, and one way it might look identical.
> 3. If you had a $5,000 budget and one engineering month, which of the limitations in this chapter would you address first, and what would you expect to learn?
