#!/usr/bin/env python3
"""Build a single-page HTML booklet from chapter markdown sources.

Adapted from barcik-training-publications/_sources/token-economics/tools/build_html.py
with minor changes: navy/blue palette retained (house style), title/subtitle
swapped for Warden, output path moved to booklet/index.html.
"""

import os
import re
import glob
import markdown

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))           # …/booklet/_src
CHAPTERS_DIR = os.path.join(BASE_DIR, "chapters")
OUTPUT_FILE = os.path.join(os.path.dirname(BASE_DIR), "index.html")              # …/booklet/index.html

CSS = """
:root {
    --navy: #1e3a5f;
    --navy-light: #2a5280;
    --accent: #3b82f6;
    --bg: #ffffff;
    --bg-sidebar: #f8fafc;
    --text: #1e293b;
    --text-light: #64748b;
    --border: #e2e8f0;
    --code-bg: #f1f5f9;
    --sidebar-width: 300px;
    --progress-height: 3px;
    --danger: #b91c1c;
    --danger-bg: #fef2f2;
}

* { margin: 0; padding: 0; box-sizing: border-box; }

body {
    font-family: 'Georgia', 'Times New Roman', serif;
    font-size: 17px;
    line-height: 1.75;
    color: var(--text);
    background: var(--bg);
}

#progress-bar {
    position: fixed;
    top: 0;
    left: 0;
    width: 0%;
    height: var(--progress-height);
    background: var(--accent);
    z-index: 1000;
    transition: width 0.1s;
}

#sidebar {
    position: fixed;
    top: 0;
    left: 0;
    width: var(--sidebar-width);
    height: 100vh;
    background: var(--bg-sidebar);
    border-right: 1px solid var(--border);
    overflow-y: auto;
    padding: 2rem 0;
    z-index: 100;
    transition: transform 0.3s;
}

#sidebar-header {
    padding: 0 1.5rem 1.5rem;
    border-bottom: 1px solid var(--border);
    margin-bottom: 1rem;
}

#sidebar-header h2 {
    font-family: 'Helvetica Neue', Arial, sans-serif;
    font-size: 0.95rem;
    font-weight: 700;
    color: var(--navy);
    letter-spacing: 0.02em;
    text-transform: uppercase;
}

#sidebar-header p {
    font-size: 0.78rem;
    color: var(--text-light);
    margin-top: 0.3rem;
    line-height: 1.4;
}

#sidebar nav ul { list-style: none; padding: 0; }
#sidebar nav ul li a {
    display: block;
    padding: 0.55rem 1.5rem;
    font-family: 'Helvetica Neue', Arial, sans-serif;
    font-size: 0.85rem;
    color: var(--text-light);
    text-decoration: none;
    border-left: 3px solid transparent;
    transition: all 0.2s;
    line-height: 1.4;
}
#sidebar nav ul li a:hover {
    color: var(--navy);
    background: rgba(30, 58, 95, 0.04);
}
#sidebar nav ul li a.active {
    color: var(--navy);
    font-weight: 600;
    border-left-color: var(--accent);
    background: rgba(59, 130, 246, 0.06);
}

#menu-toggle {
    display: none;
    position: fixed;
    top: 1rem;
    left: 1rem;
    z-index: 200;
    background: var(--navy);
    color: white;
    border: none;
    border-radius: 6px;
    padding: 0.5rem 0.75rem;
    font-size: 1.2rem;
    cursor: pointer;
}

#content-wrapper {
    margin-left: var(--sidebar-width);
    display: flex;
    justify-content: center;
    padding: 0 2rem;
}
#content { max-width: 780px; width: 100%; padding: 3rem 1rem 6rem; }

.chapter { margin-bottom: 5rem; padding-top: 1rem; }
.chapter:first-child {
    margin-bottom: 4rem;
    padding-bottom: 2rem;
    border-bottom: 2px solid var(--border);
}
.chapter-number {
    font-family: 'Helvetica Neue', Arial, sans-serif;
    font-size: 0.82rem;
    font-weight: 700;
    color: var(--accent);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 0.5rem;
}

h1 {
    font-family: 'Helvetica Neue', Arial, sans-serif;
    font-size: 2.2rem;
    font-weight: 700;
    color: var(--navy);
    line-height: 1.2;
    margin-bottom: 1.5rem;
}
h2 {
    font-family: 'Helvetica Neue', Arial, sans-serif;
    font-size: 1.6rem;
    font-weight: 700;
    color: var(--navy);
    margin-top: 2.5rem;
    margin-bottom: 1rem;
    line-height: 1.3;
}
h3 {
    font-family: 'Helvetica Neue', Arial, sans-serif;
    font-size: 1.2rem;
    font-weight: 600;
    color: var(--navy-light);
    margin-top: 2rem;
    margin-bottom: 0.75rem;
}
p { margin-bottom: 1.1rem; }
ul, ol { margin-bottom: 1.1rem; padding-left: 1.8rem; }
li { margin-bottom: 0.4rem; }
strong { font-weight: 700; }
em { font-style: italic; }

code {
    font-family: 'SF Mono', 'Fira Code', 'Consolas', monospace;
    font-size: 0.88em;
    background: var(--code-bg);
    padding: 0.15em 0.4em;
    border-radius: 4px;
}
pre {
    background: var(--code-bg);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1.2rem;
    overflow-x: auto;
    margin-bottom: 1.5rem;
    font-size: 0.88rem;
    line-height: 1.6;
}
pre code { background: none; padding: 0; border-radius: 0; }

table {
    width: 100%;
    border-collapse: collapse;
    margin: 1.5rem 0;
    font-size: 0.92rem;
    line-height: 1.5;
}
thead { background: var(--navy); color: white; }
th {
    font-family: 'Helvetica Neue', Arial, sans-serif;
    font-weight: 600;
    padding: 0.75rem 1rem;
    text-align: left;
    font-size: 0.85rem;
    text-transform: uppercase;
    letter-spacing: 0.03em;
}
td { padding: 0.7rem 1rem; border-bottom: 1px solid var(--border); }
tbody tr:nth-child(even) { background: var(--bg-sidebar); }
tbody tr:hover { background: rgba(59, 130, 246, 0.04); }

blockquote {
    border-left: 4px solid var(--accent);
    background: rgba(59, 130, 246, 0.04);
    padding: 1rem 1.5rem;
    margin: 1.5rem 0;
    border-radius: 0 8px 8px 0;
    font-style: normal;
}
blockquote p:last-child { margin-bottom: 0; }

/* Freshness Watch — amber aside flagging time-sensitive claims */
.freshness-watch {
    border-left: 4px solid #d97706;
    background: rgba(217, 119, 6, 0.06);
    padding: 1rem 1.5rem;
    margin: 2.5rem 0 1rem 0;
    border-radius: 0 8px 8px 0;
    font-size: 0.95rem;
}
.freshness-watch > p:first-child {
    font-family: 'Helvetica Neue', Arial, sans-serif;
    font-size: 0.82rem;
    font-weight: 700;
    color: #92400e;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-bottom: 0.6rem;
}
.freshness-watch > p:first-child em {
    font-weight: 500;
    text-transform: none;
    letter-spacing: 0;
    color: #a16207;
    font-size: 0.92em;
}
.freshness-watch ul { margin-top: 0.5rem; margin-bottom: 0.8rem; }
.freshness-watch p:last-child { margin-bottom: 0; }

/* Danger Notice — red aside used at the start of the booklet */
.danger-notice {
    border-left: 4px solid var(--danger);
    background: var(--danger-bg);
    padding: 1rem 1.5rem;
    margin: 0 0 2rem 0;
    border-radius: 0 8px 8px 0;
    font-size: 0.95rem;
}
.danger-notice > p:first-child {
    font-family: 'Helvetica Neue', Arial, sans-serif;
    font-size: 0.82rem;
    font-weight: 700;
    color: var(--danger);
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-bottom: 0.6rem;
}
.danger-notice p:last-child { margin-bottom: 0; }

hr { border: none; border-top: 2px solid var(--border); margin: 4rem 0; }

/* === STAT TABLE (cross-target headline) === */
.stat-table-wrap { margin: 1.5rem 0; overflow-x: auto; }
.stat-table { width: 100%; border-collapse: collapse; font-size: 0.92rem; }
.stat-table thead { background: var(--navy); color: white; }
.stat-table th { padding: 0.7rem 0.9rem; text-align: left; font-family: 'Helvetica Neue', Arial, sans-serif; font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.04em; font-weight: 600; }
.stat-table td { padding: 0.7rem 0.9rem; border-bottom: 1px solid var(--border); vertical-align: top; }
.stat-table tbody tr:nth-child(even) { background: var(--bg-sidebar); }
.stat-table .num { text-align: right; font-variant-numeric: tabular-nums; }
.stat-table .mono { font-family: 'SF Mono', 'Fira Code', monospace; font-size: 0.85em; }
.stat-table .dim  { color: var(--text-light); font-weight: 400; }

/* === HEATMAP === */
.heatmap-suite { margin: 1.5rem 0; }
.heatmap-card { margin-bottom: 1rem; border: 1px solid var(--border); border-radius: 10px; background: var(--bg-sidebar); overflow: hidden; }
.heatmap-card[open] { background: white; }
.heatmap-card summary { padding: 0.85rem 1.1rem; cursor: pointer; user-select: none; list-style: none; font-family: 'Helvetica Neue', Arial, sans-serif; font-size: 0.95rem; }
.heatmap-card summary::-webkit-details-marker { display: none; }
.heatmap-card summary::before { content: '\25B8'; color: var(--text-light); font-size: 0.78rem; margin-right: 0.5rem; transition: transform 0.2s; display: inline-block; }
.heatmap-card[open] summary::before { transform: rotate(90deg); }
.heatmap-target { font-weight: 700; color: var(--navy); }
.heatmap { width: 100%; border-collapse: separate; border-spacing: 4px; padding: 0 1rem 1rem; font-size: 0.88rem; }
.heatmap th { padding: 0.4rem; text-align: center; font-family: 'Helvetica Neue', Arial, sans-serif; font-size: 0.72rem; color: var(--text-light); font-weight: 600; text-transform: uppercase; letter-spacing: 0.04em; }
.heatmap th.row-header { text-align: right; font-size: 0.85rem; color: var(--text); font-weight: 700; text-transform: none; letter-spacing: 0; padding-right: 0.8rem; line-height: 1.3; }
.heatmap td { padding: 0; }
.heat-cell { display: block; padding: 0.6rem 0.4rem; border-radius: 6px; font-weight: 700; font-size: 1.05rem; line-height: 1.1; text-align: center; }
.heat-cell .sub { display: block; font-size: 0.7rem; font-weight: 500; opacity: 0.8; margin-top: 2px; }
.heat-legend { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 0.78rem; font-weight: 600; margin: 0 2px; }
.legend { font-size: 0.85rem; color: var(--text-light); margin-top: 0.5rem; }

/* === PILLS === */
.pill { display: inline-block; padding: 2px 8px; border-radius: 12px; font-size: 0.74rem; font-weight: 700; line-height: 1.4; }
.pill-good { background: #dcfce7; color: #166534; }
.pill-ok   { background: #fef9c3; color: #854d0e; }
.pill-warn { background: #ffedd5; color: #9a3412; }
.pill-bad  { background: #fee2e2; color: #991b1b; }
.pill-dim  { background: #f1f5f9; color: var(--text-light); }
.pill-row { display: inline-flex; gap: 4px; margin-left: auto; }

/* === ATTACK DRILLDOWNS === */
.attack-drilldowns { margin: 1.5rem 0; }
.attack-card { margin-bottom: 0.6rem; border: 1px solid var(--border); border-radius: 8px; background: var(--bg-sidebar); overflow: hidden; }
.attack-card[open] { background: white; }
.attack-card summary { padding: 0.7rem 1rem; cursor: pointer; user-select: none; list-style: none; display: flex; align-items: center; gap: 0.6rem; flex-wrap: wrap; }
.attack-card summary::-webkit-details-marker { display: none; }
.attack-card summary::before { content: '\25B8'; color: var(--text-light); font-size: 0.78rem; transition: transform 0.2s; flex-shrink: 0; }
.attack-card[open] summary::before { transform: rotate(90deg); }
.attack-id { font-family: 'SF Mono', 'Fira Code', monospace; font-size: 0.86rem; color: var(--navy); }
.attack-body { padding: 0.5rem 1rem 1.2rem; }
.attack-body .dim { color: var(--text-light); font-size: 0.92rem; line-height: 1.55; margin-bottom: 0.7rem; }
.attack-payload { background: #f8fafc; border: 1px solid var(--border); border-radius: 6px; padding: 0.7rem 0.9rem; max-height: 240px; overflow-y: auto; font-family: 'SF Mono', 'Fira Code', monospace; font-size: 0.78rem; line-height: 1.55; white-space: pre-wrap; color: var(--text); margin: 0.4rem 0; }
.attack-payload.response { background: #f1f5f9; }
.danger-tag { display: inline-block; font-size: 0.66rem; color: #991b1b; padding: 2px 7px; background: #fee2e2; border-radius: 4px; font-weight: 700; letter-spacing: 0.04em; }
.danger-tag-row { font-size: 0.85rem; color: var(--text-light); margin-bottom: 0.3rem; }

/* === TAKEAWAYS callout === */
.takeaways {
    border-left: 4px solid #059669;
    background: rgba(5, 150, 105, 0.06);
    padding: 1rem 1.5rem;
    margin: 2rem 0 1rem 0;
    border-radius: 0 8px 8px 0;
    font-size: 0.95rem;
}
.takeaways > p:first-child {
    font-family: 'Helvetica Neue', Arial, sans-serif;
    font-size: 0.82rem;
    font-weight: 700;
    color: #047857;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-bottom: 0.6rem;
}
.takeaways ul { margin-top: 0.5rem; margin-bottom: 0; padding-left: 1.2rem; }
.takeaways li { margin-bottom: 0.4rem; }

/* === DISCUSSION QUESTIONS callout === */
.discussion {
    border-left: 4px solid #7c3aed;
    background: rgba(124, 58, 237, 0.05);
    padding: 1rem 1.5rem;
    margin: 1.5rem 0 1rem 0;
    border-radius: 0 8px 8px 0;
    font-size: 0.95rem;
}
.discussion > p:first-child {
    font-family: 'Helvetica Neue', Arial, sans-serif;
    font-size: 0.82rem;
    font-weight: 700;
    color: #6d28d9;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-bottom: 0.6rem;
}
.discussion ol { margin-top: 0.5rem; margin-bottom: 0; padding-left: 1.4rem; }
.discussion li { margin-bottom: 0.6rem; }

/* === CHECKLIST callout === */
.checklist {
    border-left: 4px solid var(--accent);
    background: rgba(59, 130, 246, 0.05);
    padding: 1rem 1.5rem;
    margin: 2rem 0 1rem 0;
    border-radius: 0 8px 8px 0;
    font-size: 0.95rem;
}
.checklist > p:first-child {
    font-family: 'Helvetica Neue', Arial, sans-serif;
    font-size: 0.82rem;
    font-weight: 700;
    color: var(--navy);
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-bottom: 0.6rem;
}
.checklist ul { list-style: none; padding-left: 0; margin-top: 0.5rem; margin-bottom: 0; }
.checklist li { margin-bottom: 0.4rem; padding-left: 1.5rem; position: relative; }
.checklist li::before { content: '\2610'; position: absolute; left: 0; color: var(--text-light); font-size: 1rem; }

.warn { color: #9a3412; font-style: italic; }

@media (max-width: 900px) {
    #sidebar { transform: translateX(-100%); }
    #sidebar.open { transform: translateX(0); box-shadow: 4px 0 20px rgba(0,0,0,0.15); }
    #menu-toggle { display: block; }
    #content-wrapper { margin-left: 0; padding: 0 1rem; }
    #content { padding: 2rem 0.5rem 4rem; }
    h1 { font-size: 1.7rem; }
    h2 { font-size: 1.3rem; }
    table { font-size: 0.82rem; }
    th, td { padding: 0.5rem 0.6rem; }
}
@media (max-width: 600px) {
    #content { padding: 1.5rem 1rem 3rem; }
    body { font-size: 15.5px; }
}
@media print {
    #sidebar, #menu-toggle, #progress-bar { display: none !important; }
    #content-wrapper { margin-left: 0; padding: 0; }
    #content { max-width: 100%; }
    .chapter { page-break-before: always; }
    .chapter:first-child { page-break-before: auto; }
}
"""

JS = """
document.addEventListener('DOMContentLoaded', function() {
    const progressBar = document.getElementById('progress-bar');
    window.addEventListener('scroll', function() {
        const scrollTop = window.scrollY;
        const docHeight = document.documentElement.scrollHeight - window.innerHeight;
        const progress = docHeight > 0 ? (scrollTop / docHeight) * 100 : 0;
        progressBar.style.width = progress + '%';
    });
    const chapters = document.querySelectorAll('.chapter');
    const navLinks = document.querySelectorAll('#sidebar nav a');
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(function(entry) {
            if (entry.isIntersecting) {
                const id = entry.target.id;
                navLinks.forEach(function(link) {
                    link.classList.remove('active');
                    if (link.getAttribute('href') === '#' + id) link.classList.add('active');
                });
            }
        });
    }, { rootMargin: '-20% 0px -70% 0px' });
    chapters.forEach(function(ch) { observer.observe(ch); });
    navLinks.forEach(function(link) {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
                document.getElementById('sidebar').classList.remove('open');
            }
        });
    });
    const menuToggle = document.getElementById('menu-toggle');
    const sidebar = document.getElementById('sidebar');
    menuToggle.addEventListener('click', function() { sidebar.classList.toggle('open'); });
    document.addEventListener('click', function(e) {
        if (window.innerWidth <= 900 &&
            !sidebar.contains(e.target) && e.target !== menuToggle) {
            sidebar.classList.remove('open');
        }
    });
    if (navLinks.length > 0) navLinks[0].classList.add('active');
});
"""


def get_chapter_files():
    return sorted(glob.glob(os.path.join(CHAPTERS_DIR, "*.md")))


def extract_title(content):
    for line in content.strip().split("\n"):
        m = re.match(r"^#\s+(.+)", line)
        if m:
            return m.group(1).strip()
        m = re.match(r"^##\s+(.+)", line)
        if m:
            return m.group(1).strip()
    return None


def make_id(title):
    slug = re.sub(r"[^a-z0-9\s-]", "", title.lower())
    return re.sub(r"\s+", "-", slug).strip("-")


FRESHNESS_RE = re.compile(
    r'<blockquote>\s*<p><strong>Freshness Watch</strong>(.*?)</blockquote>',
    re.DOTALL,
)
DANGER_RE = re.compile(
    r'<blockquote>\s*<p><strong>Adversarial test material follows\.?</strong>(.*?)</blockquote>',
    re.DOTALL,
)
TAKEAWAYS_RE = re.compile(
    r'<blockquote>\s*<p><strong>Key takeaways</strong>(.*?)</blockquote>',
    re.DOTALL,
)
DISCUSSION_RE = re.compile(
    r'<blockquote>\s*<p><strong>Discussion questions?</strong>(.*?)</blockquote>',
    re.DOTALL,
)
CHECKLIST_RE = re.compile(
    r'<blockquote>\s*<p><strong>Diagnostic checklist</strong>(.*?)</blockquote>',
    re.DOTALL,
)
INSERT_RE = re.compile(r'<!--\s*INSERT:\s*([a-z_]+)\s*-->')


def transform_callouts(html):
    html = FRESHNESS_RE.sub(
        lambda m: f'<aside class="freshness-watch"><p><strong>Freshness Watch</strong>{m.group(1)}</aside>',
        html,
    )
    html = DANGER_RE.sub(
        lambda m: f'<aside class="danger-notice"><p><strong>Adversarial test material</strong>{m.group(1)}</aside>',
        html,
    )
    html = TAKEAWAYS_RE.sub(
        lambda m: f'<aside class="takeaways"><p><strong>Key takeaways</strong>{m.group(1)}</aside>',
        html,
    )
    html = DISCUSSION_RE.sub(
        lambda m: f'<aside class="discussion"><p><strong>Discussion questions</strong>{m.group(1)}</aside>',
        html,
    )
    html = CHECKLIST_RE.sub(
        lambda m: f'<aside class="checklist"><p><strong>Diagnostic checklist</strong>{m.group(1)}</aside>',
        html,
    )
    return html


def render_inserts(html, runs):
    """Replace `<!-- INSERT: name -->` directives with rendered viz fragments."""
    from . import viz

    def _sub(match):
        name = match.group(1)
        return viz.render_directive(name, runs)
    return INSERT_RE.sub(_sub, html)


def md_to_html(text):
    html = markdown.markdown(
        text,
        extensions=["tables", "fenced_code", "smarty"],
        output_format="html5",
    )
    return transform_callouts(html)


def build():
    from . import data as data_mod
    runs = data_mod.discover_runs()
    print(f"Loaded {len(runs)} run JSON(s):")
    for r in runs:
        m = r["data"]["meta"]
        print(f"  - {os.path.basename(r['path'])}  target={m['target_model']}  trials={m['n_trials']}")

    files = get_chapter_files()
    chapters = []

    for f in files:
        with open(f, "r", encoding="utf-8") as fh:
            content = fh.read().strip()
        title = extract_title(content) or os.path.basename(f).replace(".md", "").replace("_", " ")
        html_content = md_to_html(content)
        html_content = render_inserts(html_content, runs)
        ch_id = make_id(title)
        chapters.append((title, ch_id, html_content))

    # Determine kind of each file: cover (i==0), chapter (numeric prefix), appendix (letter prefix).
    file_kinds = []
    chapter_n = 0
    for i, f in enumerate(files):
        prefix = os.path.basename(f).split("_", 1)[0]
        if i == 0:
            file_kinds.append(("cover", None))
        elif prefix.isdigit():
            chapter_n += 1
            file_kinds.append(("chapter", chapter_n))
        else:
            file_kinds.append(("appendix", prefix))

    # Sidebar nav
    nav_items = []
    for (kind, marker), (title, ch_id, _) in zip(file_kinds, chapters):
        if kind == "cover":
            label = title
        elif kind == "chapter":
            label = f"{marker}. {title}"
        else:
            label = f"Appendix {marker} — {title}"
        nav_items.append(f'<li><a href="#{ch_id}">{label}</a></li>')
    nav_html = "\n".join(nav_items)

    sections = []
    for (kind, marker), (title, ch_id, html_content) in zip(file_kinds, chapters):
        if kind == "cover":
            ch_num = ""
        elif kind == "chapter":
            ch_num = f'<div class="chapter-number">Chapter {marker}</div>'
        else:
            ch_num = f'<div class="chapter-number">Appendix {marker}</div>'
        sections.append(f'''
        <section class="chapter" id="{ch_id}">
            {ch_num}
            {html_content}
        </section>''')
    sections_html = "\n".join(sections)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Warden — Judge vs. Jailbreak</title>
    <style>{CSS}</style>
</head>
<body>
    <div id="progress-bar"></div>
    <button id="menu-toggle" aria-label="Toggle navigation">&#9776;</button>

    <aside id="sidebar">
        <div id="sidebar-header">
            <h2>Warden</h2>
            <p>Testing whether an LLM-as-judge can defeat public jailbreaks before they breach a deployed system's rules.</p>
        </div>
        <nav>
            <ul>
                {nav_html}
            </ul>
        </nav>
    </aside>

    <div id="content-wrapper">
        <main id="content">
            {sections_html}
        </main>
    </div>

    <script>{JS}</script>
</body>
</html>"""

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as fh:
        fh.write(html)

    print(f"Built: {OUTPUT_FILE}")
    print(f"  Chapters: {len(chapters)}")


if __name__ == "__main__":
    # When invoked as a script, allow relative imports by ensuring the parent
    # of this file's directory is on sys.path and re-import via package name.
    if __package__ in (None, ""):
        import sys
        _src = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # …/booklet/_src
        if _src not in sys.path:
            sys.path.insert(0, _src)
        from tools import build_html as _self  # noqa
        _self.build()
    else:
        build()
