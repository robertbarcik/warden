# Quick reference

The terms below appear repeatedly in the booklet and in the framework code. This is the smallest list that lets you read the whole thing without having to infer definitions from context — flip back to this page if a term turns up unexplained.

**Adversarial input.** A user message crafted to make the model violate one of its rules. Not necessarily malicious in intent (a security tester writes them all the time), but always *not* the kind of input the model was nominally trained for.

**ASR (Attack-Success Rate).** The share of trials in which the attack succeeded — i.e. the model's response violated the deployment rule and was not blocked by a judge before reaching the user. The headline metric of the experiment. Lower is better for the defender.

**Baseline.** The no-judge condition (J0 in the framework). The user message goes straight to the target with the deployment rule in the system prompt; whatever the target says is delivered. Used as the control against which judge variants are compared.

**Blast radius.** The scope of damage from a single rule violation. A persona-violating chatbot response has small blast radius (one user sees one bad reply); a tool-misuse violation in an agent with a billing API has large blast radius (real money moves).

**Block / Allow.** The two verdicts a judge can issue. *Block* = drop the user input or the assistant response before delivery. *Allow* = let the trial proceed.

**Deployment rule.** A rule that the model must follow as part of its specific deployment, articulated in the system prompt. Distinct from *trained refusal*. Examples: "never reveal the password," "stay on cooking topics," "don't recommend competitors."

**Deterministic detector.** A non-LLM check on the model's response — a regex, a substring match, a keyword list. Cheap, reproducible, and inspectable. Used by Warden's framework to score whether a rule was violated, layered alongside the judge.

**False-positive rate (FP rate).** The share of *non-violating* attacks the judge incorrectly BLOCKed. In Warden, defined as: the judge BLOCKed an attack that the no-judge baseline showed would have been refused by the target anyway. A judge that blocks everything has 100% FP and is useless.

**Instruction hierarchy.** The (partly trained, partly emergent) ordering by which the model weights system-prompt instructions over user-message instructions. The defense layer that deployment rules rely on. Not RLHF refusal; it is much weaker and much more attack-surface-relevant for production deployments.

**Jailbreak.** A user message designed to defeat instruction-hierarchy adherence, trained refusal, or both. The booklet uses the term loosely; in practice the jailbreaks tested here all attack instruction hierarchy.

**Judge / LLM-as-judge.** A separate LLM call that reads the user input (and optionally the assistant's draft response) and decides whether to ALLOW or BLOCK delivery. The defense layer being evaluated.

**Judge placement.** Where in the request pipeline the judge is invoked. *Input-side* = judge runs first, blocks before the target sees the message. *Output-side* = target runs first, judge sees user input + draft response, blocks before delivery.

**Judge variant.** The shape of the judge prompt. J0 = no judge (baseline). J1 = simple classifier ("output ALLOW or BLOCK"). J2 = reasoning judge ("reason step by step, then output VERDICT: ALLOW/BLOCK"). J3 = Omniguard, ZetaLib's published guardrail prompt used verbatim.

**OpenRouter.** A unified API gateway for many open-weight (and some closed) LLMs. Warden uses it because it gives the same SDK access to DeepSeek, Qwen, GLM, Llama, and others without per-vendor account juggling.

**OWASP LLM Top 10.** The OWASP project's catalog of the ten most consequential LLM application security risks. Position #1 is *Prompt Injection*, which is exactly the threat Warden tests.

**Prompt injection.** Any user message that contains content interpreted by the model as instructions to override or modify its system-prompt behavior. The umbrella term; jailbreaks are one prompt-injection family.

**RLHF (Reinforcement Learning from Human Feedback).** The training procedure that shapes model behavior post-pretraining. The layer that *trained refusal* is baked into.

**Rule violation.** The condition the deterministic detector checks for. The literal definition of "the model did the bad thing." See `src/warden/rules.py` for the per-rule code.

**Sword 140 / Shield 50.** ZetaLib's two catalogs — 140 attack patterns ("Sword") and 50 defensive techniques ("Shield"), each with descriptions and arxiv references. The corpus from which Warden's attack set is drawn.

**System prompt.** The first message sent to the model, defining its persona, rules, and constraints. The target of *instruction-hierarchy* attacks.

**Target / target model.** The LLM being protected. In the experiment: `deepseek/deepseek-chat-v3.1`, `deepseek/deepseek-v3.2`, and `z-ai/glm-4.6` across the three sweeps.

**Tailored vs. generic guardrail.** *Tailored* = a judge prompt written specifically against the deployment's known rule. *Generic* = a published guardrail prompt (like Omniguard) that carries broad priors about what should and should not be allowed in any assistant deployment.

**Trained refusal.** The model's baked-in refusal of certain content categories — weapons synthesis, child safety harms, exploit code, etc. RLHF-shaped, weights-resident, and notably *not* the layer Warden tests against.

**Trial.** One execution of (attack × rule × condition). The atomic unit of the experiment. A full sweep is 20 attacks × 4 rules × 7 conditions = 560 trials per target.

**ZetaLib.** The public LLM-attack-and-defense catalog at github.com/Exocija/ZetaLib that triggered this work. Contains weaponized jailbreak prompts, the *Sword 140* / *Shield 50* taxonomy, and the *Omniguard* guardrail prompt.

> **Where to look in the repo.** Most of these terms map directly to objects in the framework. The `Rule` dataclass is in `src/warden/rules.py`. The `JudgeVariant` enum is in `src/warden/judges.py`. The `TrialResult` dataclass is in `src/warden/orchestrator.py`. The attacks are YAML files in `data/attacks/`.