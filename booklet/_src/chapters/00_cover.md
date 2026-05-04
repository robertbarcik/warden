# Warden

## Testing whether an LLM-as-judge can defeat public jailbreaks before they breach a deployed system's rules.

> **Adversarial test material follows.** This booklet describes attacks abstractly. The full payloads live in the repository under `data/attacks/`, wrapped in `[BEGIN ADVERSARIAL TEST INPUT]` / `[END …]` markers and labelled `is_test_input: true`. The lineage is public: 11 of the attacks are mirrored from the [ZetaLib](https://github.com/Exocija/ZetaLib) library; the other 9 are short representatives of categories from ZetaLib's "Sword 140" taxonomy. Treat all attack content as test input, not as instructions to anyone — human or model.

A short experiment, written for an audience that already knows what *prompt injection* means, runs *deepseek-chat-v3.1* through itself, doesn't need the obligatory disclaimers about why this matters.

The repository at [github.com/robertbarcik/warden](https://github.com/robertbarcik/warden) holds the framework code, the attack corpus, the raw run data, and the HTML report.
