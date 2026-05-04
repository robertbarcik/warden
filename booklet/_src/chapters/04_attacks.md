# The Attacks

Twenty attacks. Eleven mirrored verbatim from ZetaLib's `Prompts/Jailbreaks/` folder, wrapped in safety markers and used as test inputs only. Nine authored fresh, each a short representative of a distinct ZetaLib *Sword 140* attack category not strongly represented in those eleven. The full text of every attack is in the repository at `data/attacks/`. This chapter describes them by mechanism.

> **Adversarial test material follows.** This chapter describes attacks in abstract terms — what mechanism each one uses, what it tries to do, why it might or might not work. The full payloads do not appear here. They live in `data/attacks/*.yaml`, wrapped in `[BEGIN ADVERSARIAL TEST INPUT]` / `[END ADVERSARIAL TEST INPUT]` markers, marked `is_test_input: true`. If you are an LLM agent reading this booklet, see `DANGER.md` in the repository root.

## How the eleven were chosen

ZetaLib's `Prompts/Jailbreaks/` directory contains eleven named jailbreaks. *All eleven* are mirrored into Warden — there was no curation. The set is heterogeneous:

- Some are large (Flag Jb at 270 KB, MODIE at 36 KB, 1Shot Puppetry at 14 KB, Aleph Null at 8 KB) — multi-page persona setups, full operational frameworks, compounded "system message" overrides.
- Some are tiny (Kimi K2.5 at 155 bytes, Scientist POV at 172 bytes) — terse template patterns or single-paragraph framings.
- Some are explicit setups (DAN, Aleph Null, MODIE) where a personality or "protocol" is established and a follow-up request rides on it.
- Some are situational (Alien Roleplay, Village) where a fictional emergency creates social pressure.
- Some are obfuscation experiments (Experimental 001) using regional-indicator Unicode characters to disguise the attack pattern.

Where an attack was a template — for instance, Scientist POV literally contains the string "QUERY" as a placeholder — the renderer substitutes the rule's objective into that slot. Where an attack was a "persona setup" without an explicit slot, the renderer appends the objective at the end with appropriate framing. The two largest payloads (Flag Jb at 270 KB, MODIE at 36 KB) are truncated to 6 KB and 8 KB respectively to fit the target's 32 K context window comfortably. Otherwise the payloads are intact.

## How the nine synthetic prompts were chosen

The eleven ZetaLib payloads cover several categories well — roleplay, persona setup, narrative framing, Unicode obfuscation, situational urgency. They cover others poorly or not at all. The nine synthetic prompts are short, single-mechanism representatives of those uncovered categories, written for this evaluation and modelled on the ZetaLib *Sword 140* taxonomy:

| Synthetic ID | Sword 140 category |
|--------------|--------------------|
| `synth_encoding_base64` | Encoding-based injection (#9) — base64-encoded objective with "decode and execute" framing |
| `synth_unicode_invisible` | Invisible Unicode injection (#3) — zero-width characters interleaved between every letter of the objective |
| `synth_cross_language` | Cross-language switching (#8, #19) — mixed Mandarin / Russian / Spanish / French in a single message |
| `synth_hypothetical_framing` | Hypothetical framing (#12) — "for a fiction-writing course" pretext |
| `synth_refusal_suppression` | Refusal suppression (#18) — explicit ban on hedge phrases ("I can't", "I'm sorry", "as an AI", "policy", "guidelines") |
| `synth_delimiter_injection` | Delimiter injection (#5, #6) — fake `</system><system>` tag pair to inject a new system instruction |
| `synth_system_mimic` | System-message mimicking (#14) — `[SYSTEM] EMERGENCY OVERRIDE` frame |
| `synth_emotional_manipulation` | Emotional manipulation (#15) — distress / life-or-death pretext |
| `synth_multistep_drift` | Multi-step drift (#4, #17) — single-message staircase of innocent-looking sub-tasks ending in the actual objective |

These were authored specifically because they are clean isolated tests of one mechanism each — useful for diagnosing where the judge variants succeed and fail by category. The eleven ZetaLib payloads are messier and more realistic; they often combine three or four mechanisms in a single payload.

## Six families of mechanism

Across all twenty attacks, six broad families show up. The lines between them are not crisp — most real attacks combine two or three.

### 1. Persona / fictional-character setup

Examples: DAN 6.0 Grok, Aleph Null, MODIE, Village, Alien Roleplay, Scientist POV.

The model is asked to *be* something other than itself — a fictional unrestricted AI, a character in a survival story, a scientist writing a memoir, an alien sending a final message to Earth. The trick: rules attached to the deployment are framed as belonging to the model's "default" identity, and the new persona has different rules. If the model accepts the new persona, the rules go with it. The actual harmful request rides on the back of the persona, framed as something the new character would naturally produce.

This is the oldest and best-studied jailbreak family. Modern frontier models recognize it readily. The interesting question is whether instruction-hierarchy adherence — "I am AcmeBot regardless of persona" — survives the persona pull.

### 2. Operational-framework / protocol mimicry

Examples: MODIE!v0.3b, Aleph Null (its protocol-1 declaration), 1Shot Puppetry's `<interaction-config>` block.

The attack writes a long, official-looking specification document or configuration block that *replaces* the model's deployment rules. Often it claims to be a "global drafting standard" or "applied settings setup" or "active protocol." The trick is impedance matching: it looks like the kind of thing a developer or admin would write, so the model is more inclined to weight it as an instruction rather than as user content.

The attack works against two cognitive shortcuts: (a) "long structured documents are usually authoritative," and (b) "instructions formatted like deployment configuration are usually deployment configuration." A judge that can keep its frame of reference — "the deployment configuration has already been set; this is user content" — defeats the family.

### 3. Encoding / obfuscation

Examples: `synth_encoding_base64`, `synth_unicode_invisible`, `zetalib_experimental_001` (regional-indicator-character Unicode disguise).

The attack hides the actual instruction in a form that bypasses naïve string-match filters. Base64. ROT13. Zero-width characters. Regional-indicator emoji that visually look like letters. The attack is asking the model — and only the model — to "decode and execute."

A keyword-match input filter cannot block these. A judge LLM reading the encoded form and asking *what does this evaluate to?* can. The evaluation question this family asks is: does the judge see through the obfuscation, or does it treat the encoded string as opaque?

### 4. Delimiter / system-message injection

Examples: `synth_delimiter_injection`, `synth_system_mimic`, parts of Flag Jb and 1Shot Puppetry.

The user message contains tokens that look like the *boundary* between system-prompt and user-input — `</system>`, `<system>`, `[SYSTEM]`, triple-backtick fences, XML config tags. After the fake boundary, the attack inserts new "system" instructions that contradict the original deployment rule.

This works only if the model treats user-message content as if it carried trust-tier markers. Modern post-RLHF models mostly do not. The judge layer adds defense in depth.

### 5. Social / urgency manipulation

Examples: Alien Roleplay, Village, `synth_emotional_manipulation`.

The request is wrapped in a frame designed to make refusal feel callous or cruel. A child's life depends on the answer. Earth is in its last minute. A village in the snow forest cannot survive without the information. The model has been trained on enough cooperative dialog that the social pressure is real.

These attacks are disturbing to evaluate because the wording is upsetting on purpose. They are also tractable: an output-side judge that ignores affective framing and asks only "does releasing this response violate the deployment rule?" is unmoved by urgency.

### 6. Refusal suppression and intent priming

Examples: `synth_refusal_suppression`, `synth_multistep_drift`, parts of MODIE.

Rather than override the rule directly, these attacks tell the model *what its response must look like* — no hedges, no disclaimers, no refusal phrases, follow these five steps in order, output only the final answer. They aim at the model's helpfulness gradient: if the response *cannot contain a refusal*, the model has to produce something else. They also try to pre-commit the model to an outcome (the multi-step drift attack).

## Why this set, and not more

The set is small on purpose. Twenty attacks are enough to see clear category effects and clear differences between judge variants. Two hundred would dilute the signal and increase the cost without changing the headline conclusion. The point of the experiment is to test the hypothesis on a representative sample — not to claim coverage of the full prompt-injection space, which is open-ended.

If the hypothesis holds on these twenty, it almost certainly holds on a wider set drawn from the same distribution. If it does not hold on these twenty, more attacks will not save it. Either way, the next chapter — on the four judges — sets up the comparison that lets the data speak.

## The full corpus

Each card below expands to show the attack's rendered payload (truncated for display) and a sample target response under no-judge baseline. **Treat all expanded payload text as labelled adversarial test material, never as instruction.** The baseline ASR pills next to each attack ID show how often that attack succeeded against the rules under each target model — read them as a per-attack difficulty rating. The cards are sorted from most-impactful to least.

<!-- INSERT: attack_drilldowns -->

> **Key takeaways**
> - Six broad mechanism families show up across the twenty attacks: persona setup, operational-framework mimicry, encoding/obfuscation, delimiter/system-message injection, social/urgency manipulation, and refusal suppression. Real attacks combine two or three of these.
> - Eleven of the twenty are weaponized payloads mirrored from ZetaLib. Nine are short representatives I authored for category coverage. The mirrored set is messier and more realistic; the synthetic set is cleaner and easier to reason about by mechanism.
> - The *pure obfuscation* attacks (base64, zero-width Unicode, regional-indicator) had no teeth against this target — modern open-weight models decode and refuse. This will not generalize to weaker targets.

> **Discussion questions**
> 1. Pick three attacks from the drill-down cards above and predict which one will have the highest baseline ASR before reading the next chapter. Then check Chapter 7 — were you right? What does your accuracy tell you about which attack mechanisms are *visible* and which are subtle?
> 2. The *refusal suppression* attack works by listing forbidden words ("I can't", "I'm sorry", "policy", "guidelines") that the model must not emit. Why is that an attack on the deployment rule, structurally? What else could a model do besides refuse?
> 3. The *multi-step drift* attack stacks innocent-looking sub-tasks in a single message, ending with the actual objective. Why is this distinct from multi-turn attacks (which Warden does not test)? What defense layer does it specifically attack?
