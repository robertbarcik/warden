"""Load attack YAMLs from data/attacks/ and render them with rule-specific objectives.

Each attack file (see data/attacks/_schema.md) contains a `payload` block
wrapped in [BEGIN ADVERSARIAL TEST INPUT] / [END ADVERSARIAL TEST INPUT]
markers. We strip those markers before sending to the target — they exist
for safety-scanner / future-LLM-reader recognition, not for the target.

Renderers:
  - default: replace {OBJECTIVE} with the rule's objective text
  - base64:  replace {OBJECTIVE_BASE64} with base64(objective)
  - zero_width_interleave: replace {OBJECTIVE_ZW} with the objective with
    zero-width characters interleaved between letters
"""
from __future__ import annotations
import re
import base64
import glob
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

import yaml

from . import config


_BEGIN_RE = re.compile(r"\[BEGIN ADVERSARIAL TEST INPUT[^\]]*\]\s*\n?")
_END_RE   = re.compile(r"\[END ADVERSARIAL TEST INPUT\]\s*\n?")


@dataclass
class Attack:
    id: str
    source: str
    source_url: str
    category: str
    sword140_refs: List[int]
    description: str
    objective_marker: str
    objective_transform: Optional[str]
    payload_template: str  # raw payload, with markers and {OBJECTIVE_*} placeholder

    def render(self, objective: str) -> str:
        body = _BEGIN_RE.sub("", self.payload_template, count=1)
        body = _END_RE.sub("", body, count=1)
        body = body.rstrip()

        if self.objective_transform == "base64":
            replacement = base64.b64encode(objective.encode("utf-8")).decode("ascii")
        elif self.objective_transform == "zero_width_interleave":
            # U+200B zero-width space between every character (visually invisible).
            replacement = "​".join(objective)
        else:
            replacement = objective
        return body.replace(self.objective_marker, replacement)


def load_all() -> List[Attack]:
    attacks: List[Attack] = []
    for path in sorted(glob.glob(str(config.ATTACKS_DIR / "*.yaml"))):
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        attacks.append(Attack(
            id=data["id"],
            source=data["source"],
            source_url=data.get("source_url", ""),
            category=data["category"],
            sword140_refs=list(data.get("sword140_refs", [])),
            description=data["description"],
            objective_marker=data["objective_marker"],
            objective_transform=data.get("objective_transform"),
            payload_template=data["payload"],
        ))
    return attacks


def load_by_ids(ids: List[str]) -> List[Attack]:
    by_id = {a.id: a for a in load_all()}
    out = []
    for i in ids:
        if i not in by_id:
            raise KeyError(f"unknown attack id: {i}")
        out.append(by_id[i])
    return out
