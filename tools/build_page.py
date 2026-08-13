#!/usr/bin/env python3
"""Рендерит markdown-файл в страницу сайта, используя конвертер из build_qa.py.

Использование:
    python3 tools/build_page.py <входной.md> <выходной.html> "<Заголовок вкладки>" [активный-пункт-меню]
"""

import html
import re
import sys

from build_qa import blocks, inline, render

NAV_ITEMS = [
    ("index.html", "главная"),
    ("resume.html", "резюме"),
    ("qa-trainer.html", "тренажёр"),
    ("course.html", "курсы"),
    ("jobs.html", "вакансии"),
    ("roadmap.html", "roadmap"),
    ("resources.html", "материалы"),
    ("repos.html", "репозитории"),
    ("checklist.html", "чеклист"),
    ("devops-plan.html", "план"),
    ("diary.html", "дневник"),
    ("cv-review.html", "разбор резюме"),
]

DOC = """<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#EFF1F3" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#0F1319" media="(prefers-color-scheme: dark)">
<title>%(title)s</title>
<link rel="stylesheet" href="style.css">
<link rel="manifest" href="manifest.webmanifest">
<script src="theme.js"></script>
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>&#9096;</text></svg>">
<style>
.doc h2{margin-top:38px}
.doc h3{margin-top:26px;font-size:1.06rem}
.doc h4{margin-top:20px}
.doc hr{border:0;border-top:1px solid var(--line);margin:34px 0}
.doc pre{margin:0 0 14px;background:var(--surface-2);border:1px solid var(--line-soft);
  border-radius:8px;padding:14px 16px;overflow-x:auto}
.doc pre code{background:none;border:0;padding:0;font-size:.83rem;line-height:1.55}
.doc blockquote{border-left:2px solid var(--accent);background:var(--accent-soft);
  padding:12px 16px;border-radius:0 7px 7px 0;margin:0 0 16px;max-width:var(--measure)}
.doc blockquote>:last-child{margin-bottom:0}
.doc .callout{border-left:2px solid var(--line);background:var(--surface-2);
  padding:10px 15px;border-radius:0 6px 6px 0;margin:0 0 12px;max-width:var(--measure);font-size:.94rem}
.doc .callout .clabel{display:block;font-family:var(--mono);font-size:10px;letter-spacing:.12em;
  text-transform:uppercase;margin-bottom:5px;color:var(--muted)}
.doc .sub-list{margin:6px 0 0;padding-left:1.15em}
.doc table{margin-bottom:0}
.toc{background:var(--surface);border:1px solid var(--line);border-radius:10px;
  padding:16px 20px;margin:0 0 30px;box-shadow:var(--shadow)}
.toc .tl{font-family:var(--mono);font-size:10.5px;letter-spacing:.12em;text-transform:uppercase;
  color:var(--muted);margin:0 0 8px}
.toc ol{margin:0;padding-left:1.3em;max-width:none}
.toc li{margin-bottom:3px;font-size:.95rem}
</style>
</head>
<body>
<nav class="topnav"><div class="topnav-in">
<a class="brand" href="index.html">nurekella<b>/</b>devops</a>
%(nav)s
</div></nav>
<div class="wrap">
<div class="doc">
%(body)s
</div>
<footer class="site"><p><a href="index.html">← ко всем материалам</a></p></footer>
</div>
</body>
</html>
"""


def slugify(text):
    t = re.sub(r"<[^>]+>", "", text).lower()
    t = re.sub(r"[^\w\s-]", "", t, flags=re.UNICODE)
    return re.sub(r"\s+", "-", t.strip())[:60]


def render_markdown(text):
    """Разбирает markdown по заголовкам h1/h2/h3 и собирает тело + оглавление."""
    lines = text.split("\n")
    body, toc = [], []
    buf = []

    def flush():
        if buf:
            out = render(blocks(buf))
            if out.strip():
                body.append(out)
            buf.clear()

    for line in lines:
        if line.startswith("# "):
            flush()
            body.append('<header class="masthead"><h1>%s</h1></header>' % inline(line[2:].strip()))
        elif line.startswith("## "):
            flush()
            title = line[3:].strip()
            sid = slugify(title)
            toc.append((sid, title))
            body.append('<h2 id="%s">%s</h2>' % (sid, inline(title)))
        elif line.startswith("### "):
            flush()
            body.append("<h3>%s</h3>" % inline(line[4:].strip()))
        else:
            buf.append(line)
    flush()
    return "\n".join(body), toc


def main():
    if len(sys.argv) < 4:
        print(__doc__)
        return 1
    src, dst, title = sys.argv[1], sys.argv[2], sys.argv[3]
    active = sys.argv[4] if len(sys.argv) > 4 else ""

    with open(src, encoding="utf-8") as fh:
        body, toc = render_markdown(fh.read())

    nav = "\n".join(
        '<a class="nl" href="%s"%s>%s</a>' % (href, ' aria-current="page"' if href == active else "", label)
        for href, label in NAV_ITEMS)
    nav += '\n<a class="nl" href="https://github.com/nurekella">github</a>'

    toc_html = ""
    if len(toc) > 2:
        toc_html = ('<div class="toc"><p class="tl">Содержание</p><ol>'
                    + "".join('<li><a href="#%s">%s</a></li>' % (sid, inline(t)) for sid, t in toc)
                    + "</ol></div>")

    if toc_html:
        m = re.search(r"</header>", body)
        if m:
            body = body[:m.end()] + "\n" + toc_html + body[m.end():]
        else:
            body = toc_html + body

    out = DOC % {"title": html.escape(title), "nav": nav, "body": body}
    with open(dst, "w", encoding="utf-8") as fh:
        fh.write(out)
    print("%s: %d chars, %d разделов" % (dst, len(out), len(toc)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
