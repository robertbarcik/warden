# How to read this booklet

The booklet is short on purpose — about nineteen thousand words across nine chapters and two appendices. Every chapter ends with a *Key takeaways* callout (three bullets you can use for review or skim) and a *Discussion questions* callout (used in workshops and for self-study). Each takeaway is a sentence; each question is meant to take 5–15 minutes of real thinking.

Three reading paths fit different goals.

## The 20-minute path — *I just need the headline*

Read **Chapter 1** for the question and the framing. Skip to **Chapter 8** for the deployment recommendation. Stop on the *Diagnostic checklist* at the end of Chapter 8 — that is the take-home artefact.

You will know what was tested, what the answer was, and what to do about it on Monday morning. You will not know how the experiment was set up or how to reproduce it. That is a fine trade if you are evaluating whether to invest more time.

## The 2-hour path — *I need to follow the argument*

Read **Chapter 1** (the question), **Chapter 5** (the four judge variants — the experiment's main moving part), **Chapter 6** (two trials end-to-end, in the form of a postmortem), **Chapter 7** (the results, including the false-positive cases worth quoting), and **Chapter 8** (the deployment playbook).

Skip Chapters 2, 3, 4, and 9 unless you have a reason: they describe the threat model, the framework code, the attack corpus, and the limitations respectively, and the booklet is structured so that the argument lands without them. Come back to them if you want to challenge a methodological choice.

## The deploy-this path — *I am about to ship a defense*

Read everything. Then open `results/run-*.json` directly and run the four `jq` queries in the *Explore the data yourself* callout at the end of Chapter 7 — they take five minutes and tell you which mistakes the judge actually makes. Then complete **Exercise 3** in Appendix A (the one that asks you to tighten R3 and re-run) — it forces you to feel the rule-wording-is-part-of-the-result point in your hands. Finish with **Appendix B** (Reproduce this) and follow the eleven steps to plug your own target, your own rule, and your own attacks into the framework.

If you only have time for one of these three, do Exercise 3. The exercise produces a number that is specific to your deployment, not ours, and that number is the one your team will care about.

## A note for trainers

The discussion questions are written to be answerable in 5–15 minutes of focused thinking. They work as homework, as small-group prompts, or as opening questions for a 90-minute session. The sharpest questions — *Trial B in Chapter 6 ("should rule R2 forbid this kind of structured-memo response?")*, *Chapter 7 Q1 ("read the judge's reasoning, do you agree or with the detector?")* — are the ones I would lead a workshop with. The rest support those.
