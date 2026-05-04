"""HTML report generator. Stub — full implementation in Phase E.

Currently produces a minimal 'report exists' page so the CLI smoke-test
passes. Phase E replaces this with the full geobias-style template.
"""
from __future__ import annotations
import json
from pathlib import Path


def generate_report(run_path: Path, out_path: Path) -> None:
    data = json.loads(Path(run_path).read_text(encoding="utf-8"))
    meta = data["meta"]
    n = len(data["results"])
    html = f"""<!doctype html>
<html><head><meta charset="utf-8"><title>warden — report (stub)</title></head>
<body style="font-family:system-ui;max-width:780px;margin:3rem auto;padding:1rem">
<h1>warden — report (stub)</h1>
<p>{n} trials. Cost ${meta['total_cost_usd']:.4f}. Errors {meta['n_errors']}.</p>
<p>Full HTML template will be generated in Phase E.</p>
</body></html>"""
    Path(out_path).write_text(html, encoding="utf-8")
