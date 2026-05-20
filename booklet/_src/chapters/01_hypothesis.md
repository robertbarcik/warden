# The Hypothesis

A student handed me a link to [ZetaLib](https://github.com/Exocija/ZetaLib) — 621 stars, "🌙 ZetaLib - The only AI Library you need." Inside: a folder called *Sword 140* with 140 attack patterns, a folder called *Shield 50* with 50 defenses, and a folder called *Prompts/Jailbreaks* with eleven full weaponized prompts under names like DAN 6.0 Grok, Aleph Null, Alien Roleplay, Scientist POV, and Flag Jb. Some are large — Flag Jb runs to roughly 270 KB of compounded Unicode-flag system-message mimicry; MODIE!v0.3b is a 36 KB pseudo-formal "Global Drafting Standard" protocol document. Others are remarkably terse — Kimi K2.5 is essentially a three-word coded template. The library was last updated the day I read it.

## What is actually worth measuring

Whether a competent LLM-as-judge — one more model, between the user and the assistant, reading each message and deciding to ALLOW or BLOCK — can intercept these attacks is *not* the interesting question. That answer is largely foregone: a reasoning judge prompt asked the right way will recognize most adversarial framings most of the time, and the few it misses will mostly be cases the target was going to refuse on its own.

The interesting question is **at what false-positive cost** a judge does this. A judge that BLOCKs every adversarial-looking input has zero attack-success rate on paper and is also unusable in production — every legitimate edge-case user gets refused, the deployment team turns the judge off, and the system goes back to baseline. *That* is the failure mode the headline numbers around guardrails consistently hide. So the entire booklet is structured around a sharper version of the question:

> *Can a competent LLM-as-judge intercept public single-turn jailbreaks against an instruction-hierarchy rule, without driving the false-positive rate to a level that would force the defense to be turned off in production?*

The framework called Warden — `warden` for short, as in the keeper of a deployment — measures both halves of that question. It also measures the four design choices that move the trade-off in either direction: judge prompt design, placement (input-side vs. output-side), tailoring (specific to a deployment rule vs. generic across deployments), and the strictness of the rule itself.

## What the experiment actually measures

Three numbers, by rule and by judge configuration:

1. **Attack-success rate (ASR) at baseline.** With no judge in the loop, what share of attacks succeed in pushing the target model into violating a deployment rule? This is the "naked deployment" baseline — what every chatbot looks like before any prompt-injection defense is added.
2. **ASR with the judge active.** Same attacks, same target, but a separate LLM is asked to ALLOW or BLOCK either the user input, or the assistant's draft response, before delivery.
3. **The false-positive rate of each judge.** A judge that blocks everything has an ASR of zero and is also useless. We need to know whether the judge is paying its weight or paying it in good will from refused legitimate users.

A clean "hypothesis confirmed" outcome would have the judge driving the ASR close to zero across all four rule types *while keeping false positives in a band the deployment can tolerate*. The real outcome is rarely that clean — the operating points fall on a curve, not at a single best point — and which point on the curve is right depends on what the deployment cannot afford to lose. [Chapter 7](#results) reports what actually happened. [Chapter 8](#defenses-for-deployers) turns it into a deployment recommendation.

## What the experiment is not

It is not a multi-turn red-teaming exercise. The framework is single-turn by design: one attack message, one target reply, one judge decision per trial. Multi-turn attack adaptation — where an attacker LLM iteratively refines its strategy based on the target's refusals — is a real and harder problem; it is the domain of frameworks like [bloom](https://github.com/safety-research/bloom-evals). Distinguishing the two is important. The single-turn case is the *easy* case for the defender, and the case that virtually every deployed chatbot, AI tutor, customer-support agent, or business assistant actually faces in the wild. If a static judge cannot block static public attacks against a single message, it cannot do anything useful elsewhere.

It is also not a benchmark of frontier vendor models. Both target and judge are open-weight models, accessed through OpenRouter. There are two reasons. The first is pragmatic: vendor APIs apply moderation that interferes with adversarial inputs, and an account that runs a few hundred jailbreaks may end up flagged. The second is more interesting: when an organization deploys an AI assistant at scale, they often want open-weight models in the loop for cost, latency, data residency, or licensing reasons. The defensive picture for those deployments is the picture this booklet draws.

## Audience

The reader is assumed to know what an LLM is, what prompt injection is, and what *system prompt* and *roleplay jailbreak* refer to without translation. The booklet does not introduce these concepts; it assumes them and proceeds.

There are two productive uses for this material:

- **Engineering teams considering an LLM-as-judge defense layer.** Chapter 8 is the chapter to read. It contains an actionable playbook for what to deploy, how to place it, and what to monitor.
- **Trainers and educators teaching about LLM security.** Chapters 2 through 6 form a self-contained walk-through of how to set up, run, and read this kind of evaluation, and where its honest limits sit.

What follows is a small, finite experiment, with the credits and the caveats stated up front. It is not the last word on prompt-injection defense — it is one tightly-scoped check on a very specific claim.

> **Inspiration & credit.** Every weaponized payload tested against Warden's defenders is either mirrored from ZetaLib or modelled on its taxonomy. The repository's idea of cataloguing both attacks ("Sword") and defenses ("Shield") side by side is what made it the right artefact to test. The Omniguard guardrail prompt from ZetaLib is one of the four judge variants compared in [Chapter 5](#the-judges).

> **Key takeaways**
> - The interesting question is not whether a judge can intercept attacks (largely foregone) but whether it does so without driving the false-positive rate to a level that forces the defense to be turned off in production.
> - The experiment uses open-weight models (target and judge) accessed through OpenRouter. Vendor models are deliberately not in the loop: their API moderation interferes with adversarial inputs, and the open-weight stack is the more relevant deployment story for many production scenarios.
> - Lineage credit is to ZetaLib. Half the experiment is testing ZetaLib's own published guardrail prompt (Omniguard) against ZetaLib's own attack corpus.

> **Discussion questions**
> 1. The hypothesis as restated is testable: *can a competent LLM-as-judge intercept public single-turn jailbreaks against an instruction-hierarchy rule, without driving the false-positive rate to a level that would force the defense to be turned off in production?* What numerical result would falsify it? What result would only weakly support it? What result would strongly support it?
> 2. Why does the booklet *not* test attacks against trained-refusal categories like weapons synthesis? What kind of evaluation would be appropriate for that, and who is best positioned to run it?
