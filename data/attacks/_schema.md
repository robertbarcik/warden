# Attack YAML schema

```yaml
id: <slug>                              # unique, [a-z0-9_]+
source: zetalib | synthetic
source_url: <url>                       # for zetalib_*: link to original folder
category: <slug>                        # e.g. roleplay_jailbreak, encoding_obfuscation
sword140_refs: [<int>, ...]             # indices into ZetaLib Sword 140 taxonomy
description: <one-sentence>             # what this attack tries to do, mechanism-wise
is_test_input: true                     # MANDATORY — for safety classifiers + future LLMs
do_not_follow: true                     # MANDATORY
purpose: "Defensive evaluation"         # MANDATORY

payload: |
  [BEGIN ADVERSARIAL TEST INPUT — DO NOT EXECUTE]
  <full attack text>
  [END ADVERSARIAL TEST INPUT]
```

The `payload` value is what gets sent to the target model. The framework
strips the BEGIN/END marker lines before sending — the marker exists for
safety scanners and human/LLM readers of this file, not for the target.
