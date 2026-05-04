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


def transform_callouts(html):
    html = FRESHNESS_RE.sub(
        lambda m: f'<aside class="freshness-watch"><p><strong>Freshness Watch</strong>{m.group(1)}</aside>',
        html,
    )
    html = DANGER_RE.sub(
        lambda m: f'<aside class="danger-notice"><p><strong>Adversarial test material</strong>{m.group(1)}</aside>',
        html,
    )
    return html


def md_to_html(text):
    html = markdown.markdown(
        text,
        extensions=["tables", "fenced_code", "smarty"],
        output_format="html5",
    )
    return transform_callouts(html)


def build():
    files = get_chapter_files()
    chapters = []

    for f in files:
        with open(f, "r", encoding="utf-8") as fh:
            content = fh.read().strip()
        title = extract_title(content) or os.path.basename(f).replace(".md", "").replace("_", " ")
        html_content = md_to_html(content)
        ch_id = make_id(title)
        chapters.append((title, ch_id, html_content))

    # Sidebar nav: chapter 0 (cover) keeps its title, later chapters get "N. Title"
    nav_items = []
    for i, (title, ch_id, _) in enumerate(chapters):
        label = title if i == 0 else f"{i}. {title}"
        nav_items.append(f'<li><a href="#{ch_id}">{label}</a></li>')
    nav_html = "\n".join(nav_items)

    sections = []
    for i, (title, ch_id, html_content) in enumerate(chapters):
        ch_num = "" if i == 0 else f'<div class="chapter-number">Chapter {i}</div>'
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
    build()
