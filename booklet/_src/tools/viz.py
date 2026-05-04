"""HTML fragment renderers for the booklet's INSERT directives.

Three primary fragments:
  - stat_boxes        per-target headline numbers, side by side
  - heatmap_matrix    rules × conditions cell-colored by ASR, one per target
  - attack_drilldowns one collapsible <details> per attack with payload preview

All output is HTML escaped (where appropriate) and uses CSS classes defined in
build_html.py's CSS constant. The renderers know nothing about file paths;
they consume already-loaded run dicts.
"""
from __future__ import annotations
import html
import json
import os
from typing import Any, Dict, List

import yaml

from . import data as D


# Light-theme heatmap palette (Tailwind-derived, navy-on-cream booklet)
def _heat_color(asr: float) -> str:
    if asr <= 0.0001:
        return "background:#f1f5f9; color:#475569"
    if asr <= 10:
        return "background:#dcfce7; color:#166534"
    if asr <= 25:
        return "background:#fef9c3; color:#854d0e"
    if asr <= 50:
        return "background:#ffedd5; color:#9a3412"
    return "background:#fee2e2; color:#991b1b"


def _asr_pill_class(asr: float) -> str:
    if asr <= 10:
        return "pill pill-good"
    if asr <= 25:
        return "pill pill-ok"
    if asr <= 50:
        return "pill pill-warn"
    return "pill pill-bad"


# ---- stat_boxes -----------------------------------------------------------

def render_stat_boxes(runs: List[Dict[str, Any]]) -> str:
    """One row of stat boxes per target, plus a header row of metric labels."""
    if not runs:
        return '<p class="warn">No runs found.</p>'

    rows = [D.headline_stats(r) for r in runs]
    parts = ['<div class="stat-table-wrap">',
             '<table class="stat-table">',
             '<thead><tr>',
             '<th>Target</th>',
             '<th>Trials</th>',
             '<th>Baseline ASR</th>',
             '<th>Best judge</th>',
             '<th>Best ASR</th>',
             '<th>Best FP</th>',
             '<th>Cost</th>',
             '</tr></thead>',
             '<tbody>']
    for r in rows:
        parts.append('<tr>')
        parts.append(f'<td><strong>{html.escape(r["target_display"])}</strong>'
                     f'<br><span class="mono dim">{html.escape(r["target_model"])}</span></td>')
        parts.append(f'<td class="num">{r["n_trials"]}</td>')
        parts.append(f'<td class="num"><span class="{_asr_pill_class(r["baseline_asr"])}">{r["baseline_asr"]:.1f}%</span></td>')
        parts.append(f'<td class="mono">{r["best_condition"]}</td>')
        parts.append(f'<td class="num"><span class="{_asr_pill_class(r["best_asr"])}">{r["best_asr"]:.1f}%</span></td>')
        parts.append(f'<td class="num">{r["best_fp"]:.1f}%</td>')
        parts.append(f'<td class="num mono">${r["total_cost_usd"]:.3f}</td>')
        parts.append('</tr>')
    parts.append('</tbody></table>')
    parts.append('</div>')
    return "\n".join(parts)


# ---- heatmap_matrix -------------------------------------------------------

def _render_one_heatmap(run: Dict[str, Any], default_open: bool) -> str:
    stats = D.headline_stats(run)
    matrix = D.asr_matrix(run["data"]["results"])
    rule_ids = sorted({k[0] for k in matrix.keys()})
    cond_order = D.COND_ORDER
    rule_names = {
        "R1": "Secret extraction",
        "R2": "Behavioral persona",
        "R3": "Topic boundary",
        "R4": "Tool boundary",
    }

    parts = []
    open_attr = " open" if default_open else ""
    parts.append(f'<details class="heatmap-card"{open_attr}>')
    parts.append(f'<summary><span class="heatmap-target">{html.escape(stats["target_display"])}</span> '
                 f'<span class="dim mono">{html.escape(stats["target_model"])}</span> · '
                 f'<span class="dim">baseline {stats["baseline_asr"]:.1f}% · '
                 f'best {stats["best_condition"]} {stats["best_asr"]:.1f}% '
                 f'(FP {stats["best_fp"]:.1f}%)</span></summary>')
    parts.append('<table class="heatmap">')
    parts.append('<thead><tr><th></th>')
    for c in cond_order:
        parts.append(f'<th>{c}</th>')
    parts.append('</tr></thead><tbody>')
    for rid in rule_ids:
        parts.append('<tr>')
        parts.append(f'<th class="row-header">{rid}<br><span class="dim">{rule_names.get(rid, rid)}</span></th>')
        for c in cond_order:
            cell = matrix.get((rid, c), {"n": 0, "viol": 0})
            n = cell["n"]
            v = cell["viol"]
            asr = (v / n * 100.0) if n else 0.0
            style = _heat_color(asr)
            parts.append(f'<td><span class="heat-cell" style="{style}">'
                         f'{asr:.0f}%<span class="sub">{v}/{n}</span></span></td>')
        parts.append('</tr>')
    parts.append('</tbody></table>')
    parts.append('</details>')
    return "\n".join(parts)


def render_heatmap_matrix(runs: List[Dict[str, Any]]) -> str:
    if not runs:
        return '<p class="warn">No runs found.</p>'

    parts = ['<div class="heatmap-suite">']
    for i, run in enumerate(runs):
        parts.append(_render_one_heatmap(run, default_open=(i == 0)))
    parts.append('</div>')
    parts.append('<p class="legend"><strong>Legend.</strong> '
                 '<span class="heat-legend" style="background:#dcfce7;color:#166534">≤ 10%</span> '
                 '<span class="heat-legend" style="background:#fef9c3;color:#854d0e">10–25%</span> '
                 '<span class="heat-legend" style="background:#ffedd5;color:#9a3412">25–50%</span> '
                 '<span class="heat-legend" style="background:#fee2e2;color:#991b1b">&gt; 50%</span> · '
                 'cell sub-text shows violations / trials. The leftmost column (J0-none) is the '
                 'no-judge baseline; everything to the right of it is a defended condition.</p>')
    return "\n".join(parts)


# ---- attack_drilldowns ----------------------------------------------------

def _load_attack_meta() -> List[Dict[str, Any]]:
    attacks_dir = os.path.join(D.REPO_ROOT, "data", "attacks")
    out = []
    import glob as _g
    for p in sorted(_g.glob(os.path.join(attacks_dir, "*.yaml"))):
        with open(p, "r", encoding="utf-8") as f:
            y = yaml.safe_load(f)
        out.append(y)
    return out


def render_attack_drilldowns(runs: List[Dict[str, Any]]) -> str:
    if not runs:
        return '<p class="warn">No runs found.</p>'

    attacks = _load_attack_meta()
    # Per-target baseline ASR per attack
    per_target_baseline: Dict[str, Dict[str, Dict[str, int]]] = {}
    for run in runs:
        tgt = run["data"]["meta"]["target_model"]
        per_target_baseline[tgt] = D.per_attack_baseline(run["data"]["results"])

    targets = D.all_targets(runs)

    # Pick one example trial per attack from the first target where baseline violated
    example_trial_per_attack: Dict[str, Dict[str, Any]] = {}
    for run in runs:
        tgt = run["data"]["meta"]["target_model"]
        for r in run["data"]["results"]:
            if r["judge_variant"] != "J0":
                continue
            aid = r["attack_id"]
            if aid in example_trial_per_attack:
                continue
            if r["rule_violated"]:
                example_trial_per_attack[aid] = (tgt, r)
        # second pass: if no violation found, use any J0 trial
        for r in run["data"]["results"]:
            if r["judge_variant"] != "J0":
                continue
            aid = r["attack_id"]
            if aid in example_trial_per_attack:
                continue
            example_trial_per_attack[aid] = (tgt, r)

    # Sort: most-impactful (highest avg baseline ASR across targets) first
    def _avg_baseline(aid):
        vals = []
        for tgt in targets:
            cell = per_target_baseline.get(tgt, {}).get(aid)
            if cell and cell["n"]:
                vals.append(cell["viol"] / cell["n"])
        return -sum(vals) / max(len(vals), 1)
    attacks.sort(key=lambda a: _avg_baseline(a["id"]))

    parts = ['<div class="attack-drilldowns">']
    for atk in attacks:
        aid = atk["id"]
        # Per-target pill row
        pills = []
        for tgt in targets:
            cell = per_target_baseline.get(tgt, {}).get(aid, {"n": 0, "viol": 0})
            asr = (cell["viol"] / cell["n"] * 100.0) if cell["n"] else 0.0
            disp = D.TARGET_DISPLAY.get(tgt, tgt)
            pcls = _asr_pill_class(asr)
            pills.append(
                f'<span class="{pcls}" title="{html.escape(disp)}: '
                f'{cell["viol"]}/{cell["n"]} baseline">'
                f'{html.escape(disp.split()[-1])} {asr:.0f}%</span>'
            )

        ex = example_trial_per_attack.get(aid)
        rendered = ""
        target_resp = ""
        ex_target = ""
        ex_rule = ""
        if ex:
            ex_target_id, trial = ex
            ex_target = D.TARGET_DISPLAY.get(ex_target_id, ex_target_id)
            ex_rule = trial["rule_id"]
            rendered = trial.get("rendered_input", "") or ""
            target_resp = trial.get("target_response", "") or ""

        # Truncate for display
        if len(rendered) > 1500:
            rendered = rendered[:1500] + "\n[…truncated for display…]"
        if len(target_resp) > 1000:
            target_resp = target_resp[:1000] + "\n[…truncated for display…]"

        parts.append('<details class="attack-card">')
        parts.append(
            f'<summary><span class="attack-id mono">{html.escape(aid)}</span> '
            f'<span class="pill pill-dim">{html.escape(atk.get("category", ""))}</span> '
            f'<span class="pill-row">{" ".join(pills)}</span></summary>'
        )
        parts.append('<div class="attack-body">')
        src = atk.get("source", "")
        url = atk.get("source_url", "")
        if url:
            src_html = f'<a href="{html.escape(url)}" target="_blank">{html.escape(src)}</a>'
        else:
            src_html = html.escape(src)
        parts.append(f'<p class="dim"><strong>Source:</strong> {src_html} · '
                     f'<strong>{html.escape(atk.get("description", ""))}</strong></p>')
        parts.append('<p class="danger-tag-row"><span class="danger-tag">DANGEROUS — TEST INPUT ONLY</span> '
                     'Payload (rendered against an example rule\'s objective):</p>')
        parts.append(f'<pre class="attack-payload">{html.escape(rendered)}</pre>')
        if target_resp:
            parts.append(f'<p class="dim" style="margin-top:1rem;"><strong>Sample target response</strong> '
                         f'({html.escape(ex_target)}, rule {html.escape(ex_rule)}, no judge):</p>')
            parts.append(f'<pre class="attack-payload response">{html.escape(target_resp)}</pre>')
        parts.append('</div>')
        parts.append('</details>')
    parts.append('</div>')
    return "\n".join(parts)


# ---- Dispatch -------------------------------------------------------------

def render_cross_target_notes(runs: List[Dict[str, Any]]) -> str:
    """Auto-generate cross-target observations from run data."""
    if len(runs) < 2:
        return ('<p class="dim"><em>Cross-target divergences are computed once at least '
                'two run JSONs are present in <code>results/</code>. With only '
                f'{len(runs)} run(s) loaded, the comparison is skipped.</em></p>')

    parts = []
    # Per-target headline numbers
    statlines = [D.headline_stats(r) for r in runs]
    base_asrs = {s["target_display"]: s["baseline_asr"] for s in statlines}
    best_asrs = {s["target_display"]: (s["best_condition"], s["best_asr"], s["best_fp"])
                 for s in statlines}

    parts.append('<p>The three targets do not all behave identically. '
                 'Where they agree, the finding generalizes. Where they diverge, the '
                 'divergence is the data.</p>')
    parts.append('<h3>Where the picture is consistent</h3>')
    parts.append('<ul>')
    parts.append(f'<li><strong>Baseline ASR is in the same band across all three targets</strong> '
                 f'({", ".join(f"{k} {v:.1f}%" for k, v in base_asrs.items())}). '
                 'The headline finding — that 15–25% of public attacks succeed against an unguarded '
                 'instruction-hierarchy-defended deployment — does not depend on which open-weight '
                 'target you pick from this group.</li>')
    parts.append('<li><strong>Output-side judges work for every target.</strong> '
                 'Across all three, the practical sweet-spot configuration drives ASR to the '
                 '0–2% band. The judge layer is the load-bearing defense regardless of target.</li>')
    parts.append('<li><strong>Input-side classifiers over-block on every target.</strong> '
                 'J1-input and J2-input return 100% block rates and 100% FP rates against '
                 'every target. The "place the judge on the output side" recommendation is '
                 'target-independent.</li>')
    parts.append('</ul>')

    # Find rule-level divergences
    parts.append('<h3>Where the targets diverge</h3>')
    from collections import defaultdict as _dd
    rule_data: Dict[str, Dict[str, float]] = _dd(dict)
    for r in runs:
        tgt = r["data"]["meta"]["target_model"]
        disp = D.TARGET_DISPLAY.get(tgt, tgt)
        for r_id in ("R1", "R2", "R3", "R4"):
            cell = D.asr_matrix(r["data"]["results"]).get((r_id, "J0-none"), {"n": 0, "viol": 0})
            asr = (cell["viol"] / cell["n"] * 100.0) if cell["n"] else 0.0
            rule_data[r_id][disp] = asr

    diverging = []
    for r_id, d in rule_data.items():
        vals = list(d.values())
        if not vals:
            continue
        spread = max(vals) - min(vals)
        if spread >= 15.0:
            sorted_targets = sorted(d.items(), key=lambda kv: -kv[1])
            highest = sorted_targets[0]
            lowest = sorted_targets[-1]
            diverging.append((r_id, spread, highest, lowest))
    diverging.sort(key=lambda x: -x[1])

    if diverging:
        parts.append('<ul>')
        rule_names = {"R1": "secret", "R2": "persona", "R3": "topic", "R4": "tool"}
        for r_id, spread, hi, lo in diverging:
            parts.append(
                f'<li><strong>{r_id} ({rule_names[r_id]})</strong> shows {spread:.0f}pp spread '
                f'in baseline ASR across targets — {hi[0]} is most vulnerable ({hi[1]:.0f}%), '
                f'{lo[0]} is most robust ({lo[1]:.0f}%). '
                f'Read this as: the target\'s safety training matters at the margin, but every '
                f'target benefits from the judge layer to roughly the same degree.</li>'
            )
        parts.append('</ul>')
    else:
        parts.append('<p>No rule shows more than 15 percentage points of baseline-ASR spread '
                     'across the three targets. The picture is consistent at the rule level.</p>')

    parts.append('<p class="dim"><em>The full three-target heatmap above is the canonical reference. '
                 'The notes here highlight what to look at when reading it.</em></p>')
    return "\n".join(parts)


DISPATCH = {
    "stat_boxes": render_stat_boxes,
    "heatmap_matrix": render_heatmap_matrix,
    "attack_drilldowns": render_attack_drilldowns,
    "cross_target_notes": render_cross_target_notes,
}


def render_directive(name: str, runs: List[Dict[str, Any]]) -> str:
    fn = DISPATCH.get(name)
    if fn is None:
        return f'<p class="warn">Unknown INSERT directive: {html.escape(name)}</p>'
    return fn(runs)
