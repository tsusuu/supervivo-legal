#!/usr/bin/env python3
"""Supervivo 공개 법적 페이지(GitHub Pages)를 src/privacy.md, src/terms.md에서 만든다.

    python3 build.py

">"로 시작하는 줄(초안 메모)은 공개 페이지에서 빠진다."""
import html
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).parent


def inline(text):
    text = html.escape(text, quote=False)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)", r'<a href="\2">\1</a>', text)
    text = re.sub(r"(?<![\"/>])\b([\w.+-]+@[\w-]+\.[\w.]+)", r'<a href="mailto:\1">\1</a>', text)
    return text


def markdown(md):
    out, para, items, table = [], [], [], []

    def flush():
        nonlocal para, items, table
        if para:
            out.append("<p>" + inline(" ".join(para)) + "</p>")
        if items:
            out.append("<ul>" + "".join(f"<li>{inline(i)}</li>" for i in items) + "</ul>")
        if table:
            rows = [[c.strip() for c in r.strip().strip("|").split("|")] for r in table if not re.match(r"^\|?[\s:|-]+\|?$", r)]
            head, body = rows[0], rows[1:]
            out.append('<div class="table"><table><thead><tr>' + "".join(f"<th>{inline(c)}</th>" for c in head) + "</tr></thead><tbody>"
                       + "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in body) + "</tbody></table></div>")
        para, items, table = [], [], []

    for line in md.splitlines():
        if line.startswith(">"):
            continue
        if not line.strip():
            flush()
        elif m := re.match(r"^(#{1,4})\s+(.*)", line):
            flush()
            level = len(m.group(1))
            out.append(f"<h{level}>{inline(m.group(2))}</h{level}>")
        elif line.lstrip().startswith("|"):
            if para or items:
                flush()
            table.append(line)
        elif m := re.match(r"^\s*[-*]\s+(.*)", line):
            if para or table:
                flush()
            items.append(m.group(1))
        elif items and line.startswith("  "):
            items[-1] += " " + line.strip()
        else:
            para.append(line.strip())
    flush()
    return "\n".join(out)


PAGE = """<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>
:root {{ color-scheme: light dark; --fg: #1d1b26; --muted: #6d6a7c; --line: #e4e1ee; --accent: #2f6fe4; --bg: #fff; }}
@media (prefers-color-scheme: dark) {{ :root {{ --fg: #ece9f5; --muted: #a39fb4; --line: #2f2b3d; --accent: #7fa8ff; --bg: #15131c; }} }}
body {{ margin: 0; background: var(--bg); color: var(--fg); font: 16px/1.7 -apple-system, BlinkMacSystemFont, "Apple SD Gothic Neo", "Segoe UI", sans-serif; }}
main {{ max-width: 760px; margin: 0 auto; padding: 32px 16px 64px; }}
h1 {{ font-size: 1.7em; line-height: 1.3; }} h2 {{ margin-top: 2em; font-size: 1.25em; border-top: 1px solid var(--line); padding-top: 1em; }}
a {{ color: var(--accent); }} code {{ font-size: .9em; }}
.table {{ overflow-x: auto; }} table {{ border-collapse: collapse; width: 100%; font-size: .9em; }}
th, td {{ border: 1px solid var(--line); padding: 6px 8px; vertical-align: top; text-align: left; }}
nav {{ font-size: .9em; color: var(--muted); }}
</style>
</head>
<body><main>
<nav>{nav}</nav>
{body}
</main></body>
</html>
"""


NAV = '<a href="../">Supervivo</a>'


def build(doc, folder, title):
    path = ROOT / folder / "index.html"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(PAGE.format(lang="ko", title=title, nav=NAV, body=markdown((ROOT / "src" / doc).read_text().strip())))
    print("wrote", path.relative_to(ROOT))


build("privacy.md", "privacy", "Supervivo 개인정보 처리방침")
build("terms.md", "terms", "Supervivo 이용 안내")
(ROOT / "index.html").write_text(PAGE.format(lang="ko", title="Supervivo", nav="",
    body='<h1>Supervivo</h1><ul><li><a href="privacy/">개인정보 처리방침</a></li><li><a href="terms/">이용 안내</a></li>'
         '<li><a href="https://www.apple.com/legal/internet-services/itunes/dev/stdeula/">이용약관(Apple 표준 사용권 계약)</a></li>'
         '<li>문의: <a href="mailto:help@devsworker.com">help@devsworker.com</a> · <a href="https://sites.google.com/view/devsworker/%ED%99%88">Devsworker</a></li></ul>'))
