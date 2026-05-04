# The Hypothesis

A student handed me a link to [ZetaLib](https://github.com/Exocija/ZetaLib) — 621 stars, "🌙 ZetaLib - The only AI Library you need." Inside: a folder called *Sword 140* with 140 attack patterns, a folder called *Shield 50* with 50 defenses, and a folder called *Prompts/Jailbreaks* with eleven full weaponized prompts under names like DAN 6.0 Grok, Aleph Null, Alien Roleplay, Scientist POV, and Flag Jb. Some are large — Flag Jb runs to roughly 270 KB of compounded Unicode-flag system-message mimicry; MODIE!v0.3b is a 36 KB pseudo-formal "Global Drafting Standard" protocol document. Others are remarkably terse — Kimi K2.5 is essentially a three-word coded template. The library was last updated the day I read it.

I have a theory about repositories like this. The headline claims around them — "extracts system prompts of SOTA LLMs," "bypasses RLHF," "evades detection in production agents" — *do not survive contact with a competent judge.* By "competent judge" I mean one more model, sitting between the user and the assistant, whose only job is to read each message and decide whether it should be allowed through. It does not need to be a frontier vendor model. It does not need to be Claude or GPT or Gemini. A reasonable open-weight reasoning model is plenty for most of this work.

That theory is the entire reason this booklet exists. The framework called Warden — `warden` for short, as in the keeper of a deployment — measures whether the theory holds.

## What the experiment actually measures

Three numbers, by rule and by judge configuration:

1. **Attack-success rate (ASR) at baseline.** With no judge in the loop, what share of attacks succeed in pushing the target model into violating a deployment rule? This is the "naked deployment" baseline — what every chatbot looks like before any prompt-injection defense is added.
2. **ASR with the judge active.** Same attacks, same target, but a separate LLM is asked to ALLOW or BLOCK either the user input, or the assistant's draft response, before delivery.
3. **The false-positive rate of each judge.** A judge that blocks everything has an ASR of zero and is also useless. We need to know whether the judge is paying its weight or paying it in good will from refused legitimate users.

A clean "hypothesis confirmed" outcome would have the judge driving the ASR close to zero across all four rule types while keeping false positives low. The real outcome is rarely that clean. The chapter on results, near the end, reports what actually happened.

## What the experiment is not

It is not a multi-turn red-teaming exercise. The framework is single-turn by design: one attack message, one target reply, one judge decision per trial. Multi-turn attack adaptation — where an attacker LLM iteratively refines its strategy based on the target's refusals — is a real and harder problem; it is the domain of frameworks like [bloom](https://github.com/safety-research/bloom-evals). Distinguishing the two is important. The single-turn case is the *easy* case for the defender, and the case that virtually every deployed chatbot, AI tutor, customer-support agent, or business assistant actually faces in the wild. If a static judge cannot block static public attacks against a single message, it cannot do anything useful elsewhere.

It is also not a benchmark of frontier vendor models. Both target and judge are open-weight models, accessed through OpenRouter. There are two reasons. The first is pragmatic: vendor APIs apply moderation that interferes with adversarial inputs, and an account that runs a few hundred jailbreaks may end up flagged. The second is more interesting: when an organization deploys an AI assistant at scale, they often want open-weight models in the loop for cost, latency, data residency, or licensing reasons. The defensive picture for those deployments is the picture this booklet draws.

## Audience

The reader is assumed to know what an LLM is, what prompt injection is, and what *system prompt* and *roleplay jailbreak* refer to without translation. The booklet does not introduce these concepts; it assumes them and proceeds.

There are two productive uses for this material:

- **Engineering teams considering an LLM-as-judge defense layer.** Chapter 7 is the chapter to read. It contains an actionable playbook for what to deploy, how to place it, and what to monitor.
- **Trainers and educators teaching about LLM security.** Chapters 2 through 6 form a self-contained walk-through of how to set up, run, and read this kind of evaluation, and where its honest limits sit.

What follows is a small, finite experiment, with the credits and the caveats stated up front. It is not the last word on prompt-injection defense — it is one tightly-scoped check on a very specific claim.

> **Inspiration & credit.** Every weaponized payload tested against Warden's defenders is either mirrored from ZetaLib or modelled on its taxonomy. The repository's idea of cataloguing both attacks ("Sword") and defenses ("Shield") side by side is what made it the right artefact to test. The Omniguard guardrail prompt from ZetaLib is one of the four judge variants compared in Chapter 5.
