#!/usr/bin/env python3
"""Собирает интерактивный тренажёр (HTML) из INTERVIEW_QA.md."""

import html
import re
import sys

SRC = "INTERVIEW_QA.md"
OUT = "docs/qa-trainer.html"

OUT_USED = []

MARKERS = ("Что проверяют", "Глубже", "Типичная ошибка", "Типичные ошибки")
ANSWER_STARTS = ("**Ответ", "**Решение", "**Как отвечать", "**Структура", "**Хорошие вопросы")


# ─────────────────────────── inline markdown ───────────────────────────

def inline(text):
    """Инлайновый markdown → HTML. Код извлекается первым, чтобы внутри него ничего не форматировалось."""
    spans = []

    def stash(m):
        spans.append(m.group(1))
        return "\x00%d\x00" % (len(spans) - 1)

    text = re.sub(r"`([^`]+)`", stash, text)
    text = html.escape(text, quote=False)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)",
                  lambda m: '<a href="%s" target="_blank" rel="noopener">%s</a>'
                            % (html.escape(m.group(2), quote=True), m.group(1)), text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<![\w*])\*([^*\n]+)\*(?![\w*])", r"<em>\1</em>", text)
    text = re.sub(r"\x00(\d+)\x00",
                  lambda m: "<code>%s</code>" % html.escape(spans[int(m.group(1))], quote=False), text)
    return text


# ─────────────────────────── block markdown ───────────────────────────

def collect_list(lines, start, top_re):
    """Собирает список от строки start. Возвращает [(текст, [подпункты])].
    Индекс строки после списка кладётся в collect_list.end."""
    items, i, n = [], start, len(lines)
    sub_re = r"^[-*]\s+"
    while i < n:
        raw = lines[i]
        s = raw.strip()
        if not s:
            break
        indented = raw.startswith(" ")
        if not indented and re.match(top_re, s):
            items.append([re.sub(top_re, "", s), []])
        elif indented and items and re.match(sub_re, s):
            items[-1][1].append(re.sub(sub_re, "", s))
        elif indented and items:
            if items[-1][1]:
                items[-1][1][-1] += " " + s
            else:
                items[-1][0] += " " + s
        else:
            break
        i += 1
    collect_list.end = i
    return items


collect_list.end = 0


def render_items(items, tag):
    parts = ["<%s>" % tag]
    for text, subs in items:
        parts.append("<li>%s" % inline(text))
        if subs:
            parts.append("<ul class=\"sub-list\">" +
                         "".join("<li>%s</li>" % inline(x) for x in subs) + "</ul>")
        parts.append("</li>")
    parts.append("</%s>" % tag)
    return "".join(parts)


def blocks(lines):
    """Разбивает строки на блоки: ('code'|'table'|'ul'|'ol'|'quote'|'p'|'h4', payload)."""
    out, i, n = [], 0, len(lines)
    while i < n:
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            i += 1
            continue

        if stripped.startswith("```"):
            lang = stripped[3:].strip()
            i += 1
            buf = []
            while i < n and not lines[i].strip().startswith("```"):
                buf.append(lines[i])
                i += 1
            i += 1
            out.append(("code", (lang, "\n".join(buf))))
            continue

        if stripped.startswith("|"):
            buf = []
            while i < n and lines[i].strip().startswith("|"):
                buf.append(lines[i].strip())
                i += 1
            out.append(("table", buf))
            continue

        if re.match(r"^[-*]\s+", line) or re.match(r"^[-*]\s+", stripped) and not line.startswith(" "):
            out.append(("ul", collect_list(lines, i, r"^[-*]\s+")))
            i = collect_list.end
            continue

        if re.match(r"^\d+\.\s+", stripped) and not line.startswith(" "):
            out.append(("ol", collect_list(lines, i, r"^\d+\.\s+")))
            i = collect_list.end
            continue

        if stripped.startswith(">"):
            buf = []
            while i < n and lines[i].strip().startswith(">"):
                buf.append(lines[i].strip().lstrip(">").strip())
                i += 1
            out.append(("quote", " ".join(buf)))
            continue

        if stripped.startswith("#### "):
            out.append(("h4", stripped[5:]))
            i += 1
            continue

        if set(stripped) <= {"-"} and len(stripped) >= 3:
            i += 1
            continue

        buf = []
        while i < n and lines[i].strip() and not lines[i].strip().startswith(("|", ">", "```", "#")) \
                and not re.match(r"^([-*]|\d+\.)\s+", lines[i].strip()):
            buf.append(lines[i].strip())
            i += 1
        out.append(("p", " ".join(buf)))
    return out


def render_table(rows):
    cells = [[c.strip() for c in r.strip("|").split("|")] for r in rows]
    if len(cells) >= 2 and set("".join(cells[1]).replace(" ", "")) <= set("-:"):
        head, body = cells[0], cells[2:]
    else:
        head, body = None, cells
    parts = ['<div class="scroller"><table>']
    if head:
        parts.append("<thead><tr>" + "".join("<th>%s</th>" % inline(c) for c in head) + "</tr></thead>")
    parts.append("<tbody>")
    for row in body:
        parts.append("<tr>" + "".join("<td>%s</td>" % inline(c) for c in row) + "</tr>")
    parts.append("</tbody></table></div>")
    return "".join(parts)


def render(bs):
    out = []
    for kind, payload in bs:
        if kind == "code":
            lang, body = payload
            out.append('<div class="scroller"><pre><code>%s</code></pre></div>'
                       % html.escape(body, quote=False))
        elif kind == "table":
            out.append(render_table(payload))
        elif kind == "ul":
            out.append(render_items(payload, "ul"))
        elif kind == "ol":
            out.append(render_items(payload, "ol"))
        elif kind == "quote":
            out.append('<blockquote>%s</blockquote>' % inline(payload))
        elif kind == "h4":
            out.append("<h4>%s</h4>" % inline(payload))
        else:
            text = payload
            marker = None
            for m in MARKERS:
                if text.startswith("`%s`" % m):
                    marker = m
                    text = text[len(m) + 2:].strip()
                    break
            if marker:
                cls = {"Что проверяют": "probe", "Глубже": "deep",
                       "Типичная ошибка": "trap", "Типичные ошибки": "trap"}[marker]
                out.append('<div class="callout %s"><span class="clabel">%s</span>%s</div>'
                           % (cls, marker, inline(text)))
            else:
                out.append("<p>%s</p>" % inline(text))
    return "\n".join(out)


def split_answer(bs):
    """Делит блоки вопроса на видимую часть и скрытый ответ."""
    for idx, (kind, payload) in enumerate(bs):
        if kind == "p" and isinstance(payload, str) and payload.startswith(ANSWER_STARTS):
            return bs[:idx], bs[idx:]
    visible = [b for b in bs if b[0] == "p" and isinstance(b[1], str)
               and b[1].startswith("`Что проверяют`")]
    hidden = [b for b in bs if b not in visible]
    return visible, hidden


# ─────────────────────────── parse the document ───────────────────────────

def parse(text):
    lines = text.split("\n")
    doc_title = ""
    sections, intro = [], []
    cur = None
    i = 0

    while i < len(lines):
        line = lines[i]
        if line.startswith("# ") and not doc_title:
            doc_title = line[2:].strip()
            i += 1
            continue
        if line.startswith("## "):
            cur = {"title": line[3:].strip(), "items": [], "lead": []}
            sections.append(cur)
            i += 1
            continue
        if line.startswith("### "):
            heading = line[4:].strip()
            m = re.match(r"^(\d+)\.\s+(.*)$", heading)
            body = []
            i += 1
            while i < len(lines) and not lines[i].startswith(("## ", "### ")):
                body.append(lines[i])
                i += 1
            cur["items"].append({
                "num": int(m.group(1)) if m else None,
                "title": m.group(2) if m else heading,
                "blocks": blocks(body),
            })
            continue
        (cur["lead"] if cur else intro).append(line)
        i += 1

    return doc_title, blocks(intro), sections


# ─────────────────────────── emit HTML ───────────────────────────

def slug(i):
    return "s%d" % i


def build(doc_title, intro_blocks, sections):
    nav, body = [], []
    total_q = 0

    for si, sec in enumerate(sections):
        qs = [it for it in sec["items"] if it["num"]]
        total_q += len(qs)
        nav.append(
            '<a href="#%s"><span class="nt">%s</span>%s</a>' % (
                slug(si), html.escape(sec["title"]),
                '<span class="nsc" data-sec="%d">—</span>' % si if qs else ""))

        body.append('<section id="%s" data-sec="%d">' % (slug(si), si))
        body.append('<div class="sect-head"><h2>%s</h2>%s</div>' % (
            html.escape(sec["title"]),
            '<div class="sect-score"><span class="bar"><span class="fill" data-secfill="%d"></span></span>'
            '<span class="mono" data-seclabel="%d">0 / %d</span></div>' % (si, si, len(qs)) if qs else ""))

        lead = render(blocks(sec["lead"]))
        if lead.strip():
            body.append('<div class="prose lead">%s</div>' % lead)

        for it in sec["items"]:
            if it["num"]:
                vis, hid = split_answer(it["blocks"])
                qid = "q%d" % it["num"]
                body.append(
                    '<article class="q" id="%s" data-q="%d" data-sec="%d" '
                    'data-text="%s">' % (
                        qid, it["num"], si,
                        html.escape(("%d %s" % (it["num"], it["title"])).lower(), quote=True)))
                body.append('<header class="qh"><span class="qn mono">%02d</span>'
                            '<h3>%s</h3><span class="mark mono" data-mark="%d"></span></header>'
                            % (it["num"], inline(it["title"]), it["num"]))
                if vis:
                    body.append('<div class="prose qvis">%s</div>' % render(vis))
                body.append('<button class="reveal" type="button" data-reveal="%d">'
                            'Показать ответ</button>' % it["num"])
                body.append('<div class="prose ans" data-ans="%d" hidden>%s</div>'
                            % (it["num"], render(hid)))
                body.append('<div class="rate" data-rate="%d">'
                            '<span class="rl mono">Оценка</span>'
                            '<button type="button" data-v="0">0 — не знаю</button>'
                            '<button type="button" data-v="1">1 — плыл</button>'
                            '<button type="button" data-v="2">2 — уверенно</button>'
                            '<button type="button" data-v="-" class="clr">×</button>'
                            '</div>' % it["num"])
                body.append("</article>")
            else:
                body.append('<div class="sub"><h3>%s</h3><div class="prose">%s</div></div>'
                            % (inline(it["title"]), render(it["blocks"])))
        body.append("</section>")

    tpl = TEMPLATE
    tpl = tpl.replace("{{TITLE}}", html.escape(doc_title))
    tpl = tpl.replace("{{NAV}}", "\n".join(nav))
    tpl = tpl.replace("{{INTRO}}", render(intro_blocks))
    tpl = tpl.replace("{{BODY}}", "\n".join(body))
    tpl = tpl.replace("{{TOTAL}}", str(total_q))
    return tpl


SITE_NAV = """<nav class="sitenav"><div class="sitenav-in">
<a class="sbrand" href="./">nurekella<b>/</b>devops</a>
<a href="./">главная</a><a href="resume.html">резюме</a>
<a href="qa-trainer.html" aria-current="page">тренажёр</a>
<a href="devops-plan.html">план</a><a href="cv-review.html">разбор резюме</a>
<a href="https://github.com/nurekella">github</a>
</div></nav>"""

SITE_NAV_CSS = """<style>
.sitenav{border-bottom:1px solid var(--line);background:var(--bg)}
.sitenav-in{max-width:1240px;margin:0 auto;padding:12px 28px;display:flex;
  align-items:center;gap:6px 18px;flex-wrap:wrap;font-family:var(--mono);font-size:12px}
.sitenav .sbrand{margin-right:auto;color:var(--ink);text-decoration:none;letter-spacing:.04em}
.sitenav .sbrand b{color:var(--accent)}
.sitenav a{color:var(--muted);text-decoration:none;padding:4px 8px;border-radius:6px;letter-spacing:.04em}
.sitenav a:hover{background:var(--surface);color:var(--accent)}
.sitenav a[aria-current="page"]{background:var(--surface);color:var(--ink);border:1px solid var(--line)}
@media (max-width:900px){.sitenav-in{padding:10px 18px}}
</style>"""

TEMPLATE = r"""<title>Тренажёр DevOps-собеседования — {{TITLE}}</title>
<style>
:root{
  --bg:#EFF1F3; --surface:#FFFFFF; --surface-2:#F7F8FA; --line:#D5DBE1; --line-soft:#E5E9ED;
  --ink:#131920; --ink-2:#3C4753; --muted:#6B7684;
  --accent:#0E6285; --accent-2:#0A4C68; --accent-soft:#E2EDF3;
  --s0:#9E2B22; --s0b:#F6E5E2; --s1:#8A5B10; --s1b:#F7EDDC; --s2:#1C6B4B; --s2b:#E1F0E8;
  --shadow:0 1px 2px rgba(19,25,32,.05),0 8px 24px -12px rgba(19,25,32,.12);
  --serif:ui-serif,Georgia,"Iowan Old Style","Times New Roman",serif;
  --sans:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;
  --mono:ui-monospace,"SF Mono","Cascadia Mono",Menlo,Consolas,"Liberation Mono",monospace;
  --measure:70ch; --rail:250px;
}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
  --bg:#0F1319; --surface:#161B23; --surface-2:#1C232D; --line:#2A323D; --line-soft:#212932;
  --ink:#E7ECF2; --ink-2:#B8C3CF; --muted:#8593A2;
  --accent:#6BB8DA; --accent-2:#9CD3EA; --accent-soft:#16303D;
  --s0:#F0897B; --s0b:#33201D; --s1:#DFAE5C; --s1b:#302617; --s2:#6DC59B; --s2b:#162C23;
  --shadow:0 1px 2px rgba(0,0,0,.4),0 8px 24px -12px rgba(0,0,0,.6);
}}
:root[data-theme="dark"]{
  --bg:#0F1319; --surface:#161B23; --surface-2:#1C232D; --line:#2A323D; --line-soft:#212932;
  --ink:#E7ECF2; --ink-2:#B8C3CF; --muted:#8593A2;
  --accent:#6BB8DA; --accent-2:#9CD3EA; --accent-soft:#16303D;
  --s0:#F0897B; --s0b:#33201D; --s1:#DFAE5C; --s1b:#302617; --s2:#6DC59B; --s2b:#162C23;
  --shadow:0 1px 2px rgba(0,0,0,.4),0 8px 24px -12px rgba(0,0,0,.6);
}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font-family:var(--sans);
  font-size:16.5px;line-height:1.62;-webkit-font-smoothing:antialiased}
a{color:var(--accent);text-underline-offset:2px}
a:hover{color:var(--accent-2)}
:focus-visible{outline:2px solid var(--accent);outline-offset:2px;border-radius:3px}
.mono{font-family:var(--mono);font-variant-numeric:tabular-nums}

/* ── score bar ── */
.topbar{position:sticky;top:0;z-index:20;background:var(--bg);
  border-bottom:1px solid var(--line);padding:10px 28px}
.topbar-in{max-width:1240px;margin:0 auto;display:flex;align-items:center;gap:18px;flex-wrap:wrap}
.score{display:flex;align-items:center;gap:12px;min-width:270px}
.score .big{font-family:var(--mono);font-size:1.35rem;letter-spacing:-.02em;color:var(--accent)}
.score .verdict{font-size:.83rem;color:var(--muted);line-height:1.3;max-width:26ch}
.meter{flex:1;min-width:120px;height:6px;background:var(--line-soft);border-radius:3px;
  overflow:hidden;display:flex}
.meter i{height:100%;width:0;transition:width .3s ease}
.meter .m2{background:var(--s2)} .meter .m1{background:var(--s1)} .meter .m0{background:var(--s0)}
.tools{display:flex;gap:7px;align-items:center;margin-left:auto;flex-wrap:wrap}
input[type=search]{font:inherit;font-size:.9rem;padding:6px 11px;border-radius:6px;
  border:1px solid var(--line);background:var(--surface);color:var(--ink);width:190px}
.chip{font-family:var(--mono);font-size:11px;letter-spacing:.04em;background:var(--surface);
  border:1px solid var(--line);color:var(--muted);padding:5px 10px;border-radius:6px;cursor:pointer}
.chip:hover{border-color:var(--accent);color:var(--accent)}
.chip.on{background:var(--accent);border-color:var(--accent);color:var(--surface)}

/* ── shell ── */
.shell{display:grid;grid-template-columns:var(--rail) minmax(0,1fr);gap:44px;
  max-width:1240px;margin:0 auto;padding:0 28px 96px;align-items:start}
.rail{position:sticky;top:64px;padding:28px 0;max-height:calc(100vh - 64px);overflow-y:auto}
.rail-title{font-family:var(--mono);font-size:10.5px;letter-spacing:.13em;text-transform:uppercase;
  color:var(--muted);margin:0 0 10px}
.rail nav{display:flex;flex-direction:column;gap:1px}
.rail a{display:flex;gap:8px;align-items:baseline;padding:5px 9px;border-radius:5px;
  color:var(--ink-2);text-decoration:none;font-size:13.5px;line-height:1.3}
.rail a:hover{background:var(--surface);color:var(--ink)}
.rail a .nt{flex:1;min-width:0}
.rail a .nsc{font-family:var(--mono);font-size:10.5px;color:var(--muted);
  font-variant-numeric:tabular-nums;white-space:nowrap}
.main{padding:28px 0 0;min-width:0}

.masthead{border-bottom:2px solid var(--ink);padding-bottom:22px;margin-bottom:30px}
.eyebrow{font-family:var(--mono);font-size:11px;letter-spacing:.15em;text-transform:uppercase;
  color:var(--accent);margin:0 0 14px}
h1{font-family:var(--serif);font-size:clamp(1.9rem,4vw,2.8rem);line-height:1.08;
  letter-spacing:-.015em;font-weight:600;margin:0 0 16px;text-wrap:balance;max-width:26ch}

section{margin:0 0 56px;scroll-margin-top:74px}
.sect-head{border-top:1px solid var(--line);padding-top:14px;margin-bottom:22px;
  display:flex;align-items:baseline;gap:20px;flex-wrap:wrap}
.sect-head h2{font-family:var(--serif);font-size:1.5rem;line-height:1.2;font-weight:600;
  letter-spacing:-.01em;margin:0;text-wrap:balance;flex:1;min-width:200px}
.sect-score{display:flex;align-items:center;gap:9px;font-size:11px;color:var(--muted)}
.sect-score .bar{width:88px;height:5px;background:var(--line-soft);border-radius:3px;overflow:hidden;display:block}
.sect-score .fill{display:block;height:100%;width:0;background:var(--accent);transition:width .3s ease}

h3{font-family:var(--sans);font-size:1.05rem;font-weight:650;margin:0;letter-spacing:-.005em}
h4{font-family:var(--sans);font-size:.98rem;font-weight:650;margin:16px 0 8px}
.prose p,.prose ul,.prose ol,.prose blockquote{margin:0 0 12px;max-width:var(--measure)}
.prose>:last-child{margin-bottom:0}
.prose ul,.prose ol{padding-left:1.25em}
.prose li{margin-bottom:6px}
.prose li::marker{color:var(--muted)}
.sub-list{margin:6px 0 0;padding-left:1.15em}
.sub-list li{margin-bottom:3px;font-size:.96em}
.prose blockquote{border-left:2px solid var(--line);padding-left:14px;color:var(--ink-2);margin-left:0}
.lead{color:var(--ink-2);margin-bottom:24px}
.sub{border-top:1px solid var(--line-soft);padding:18px 0}
.sub h3{margin-bottom:10px}
code{font-family:var(--mono);font-size:.855em;background:var(--surface-2);
  border:1px solid var(--line-soft);border-radius:4px;padding:.08em .34em}
pre{margin:0;background:var(--surface-2);border:1px solid var(--line-soft);border-radius:8px;
  padding:14px 16px;overflow-x:auto}
pre code{background:none;border:0;padding:0;font-size:.83rem;line-height:1.55}
.scroller{overflow-x:auto;margin:0 0 14px;max-width:100%}
table{border-collapse:collapse;width:100%;font-size:.92rem;background:var(--surface)}
th,td{text-align:left;padding:10px 13px;border-bottom:1px solid var(--line-soft);vertical-align:top}
thead th{font-family:var(--mono);font-size:10.5px;letter-spacing:.09em;text-transform:uppercase;
  color:var(--muted);font-weight:500;border-bottom:1px solid var(--line);white-space:nowrap}
tbody tr:last-child td{border-bottom:0}

/* ── callouts ── */
.callout{border-left:2px solid var(--line);padding:10px 15px;border-radius:0 6px 6px 0;
  margin:0 0 12px;font-size:.94rem;max-width:var(--measure);background:var(--surface-2)}
.callout .clabel{display:block;font-family:var(--mono);font-size:10px;letter-spacing:.12em;
  text-transform:uppercase;margin-bottom:5px;color:var(--muted)}
.callout.probe{border-left-color:var(--accent);background:var(--accent-soft)}
.callout.probe .clabel{color:var(--accent)}
.callout.deep{border-left-color:var(--s2);background:var(--s2b)}
.callout.deep .clabel{color:var(--s2)}
.callout.trap{border-left-color:var(--s0);background:var(--s0b)}
.callout.trap .clabel{color:var(--s0)}

/* ── question card ── */
.q{background:var(--surface);border:1px solid var(--line);border-radius:10px;
  padding:18px 20px;margin:0 0 14px;box-shadow:var(--shadow);scroll-margin-top:74px}
.q.hide{display:none}
.qh{display:grid;grid-template-columns:34px minmax(0,1fr) auto;gap:12px;align-items:baseline;
  margin-bottom:12px}
.qn{font-size:13px;color:var(--muted)}
.mark{font-size:11px;letter-spacing:.05em;padding:1px 7px;border-radius:4px;white-space:nowrap;
  border:1px solid transparent}
.q[data-v="0"] .mark{background:var(--s0b);color:var(--s0);border-color:var(--s0)}
.q[data-v="1"] .mark{background:var(--s1b);color:var(--s1);border-color:var(--s1)}
.q[data-v="2"] .mark{background:var(--s2b);color:var(--s2);border-color:var(--s2)}
.q[data-v="0"]{border-left:3px solid var(--s0)}
.q[data-v="1"]{border-left:3px solid var(--s1)}
.q[data-v="2"]{border-left:3px solid var(--s2)}
.qvis{margin-bottom:12px}
.reveal{font-family:var(--mono);font-size:11.5px;letter-spacing:.06em;text-transform:uppercase;
  background:var(--surface-2);border:1px dashed var(--line);color:var(--accent);
  padding:8px 14px;border-radius:7px;cursor:pointer;width:100%}
.reveal:hover{border-color:var(--accent);background:var(--accent-soft)}
.reveal[hidden]{display:none}
.ans{margin-top:6px;padding-top:14px;border-top:1px solid var(--line-soft)}
.rate{display:flex;align-items:center;gap:6px;margin-top:14px;padding-top:12px;
  border-top:1px solid var(--line-soft);flex-wrap:wrap}
.rate .rl{font-size:10px;letter-spacing:.12em;text-transform:uppercase;color:var(--muted);margin-right:4px}
.rate button{font-family:var(--mono);font-size:11px;background:var(--surface-2);
  border:1px solid var(--line);color:var(--muted);padding:5px 10px;border-radius:6px;cursor:pointer}
.rate button:hover{border-color:var(--accent);color:var(--accent)}
.rate button.clr{margin-left:auto;padding:5px 9px}
.q[data-v="0"] .rate button[data-v="0"]{background:var(--s0);border-color:var(--s0);color:var(--surface)}
.q[data-v="1"] .rate button[data-v="1"]{background:var(--s1);border-color:var(--s1);color:var(--surface)}
.q[data-v="2"] .rate button[data-v="2"]{background:var(--s2);border-color:var(--s2);color:var(--surface)}
.panel{background:var(--surface);border:1px solid var(--line);border-radius:10px;
  padding:16px 18px;margin:0 0 20px;box-shadow:var(--shadow)}
.panel[hidden]{display:none}
.panel .pt{font-family:var(--mono);font-size:10.5px;letter-spacing:.12em;text-transform:uppercase;
  color:var(--accent);margin:0 0 8px}
.panel .pd{font-size:.94rem;color:var(--ink-2);margin:0 0 12px;max-width:var(--measure)}
.panel .prow{display:flex;flex-wrap:wrap;gap:7px;align-items:center}
.panel textarea{width:100%;font-family:var(--mono);font-size:11px;line-height:1.5;
  background:var(--surface-2);color:var(--ink-2);border:1px solid var(--line);
  border-radius:7px;padding:9px 11px;margin:0 0 10px;resize:vertical;word-break:break-all}
.panel .pmsg{font-family:var(--mono);font-size:11px;color:var(--s2)}
.panel table{margin:0}
.panel .big2{font-family:var(--mono);font-size:1.6rem;color:var(--accent);letter-spacing:-.02em}
.timer{font-family:var(--mono);font-size:13px;font-variant-numeric:tabular-nums;
  background:var(--accent-soft);color:var(--accent);border:1px solid var(--accent);
  border-radius:6px;padding:4px 9px;white-space:nowrap}
.timer[hidden]{display:none}
.timer.low{background:var(--s0b);color:var(--s0);border-color:var(--s0)}
#dueN:empty{display:none}
.reveal[disabled]{opacity:.5;cursor:not-allowed;border-style:solid}
.reveal[disabled]:hover{border-color:var(--line);background:var(--surface-2)}
body.cards .rail,body.cards .keyhint,body.cards section .sect-head,
body.cards .masthead,body.cards .progress{display:none}
body.cards .shell{grid-template-columns:minmax(0,1fr);max-width:760px}
body.cards .q{display:none}
body.cards .q.active{display:block;margin-top:12px}
body.cards .cardnav{display:flex}
.cardnav{display:none;position:sticky;bottom:0;gap:10px;padding:12px 0 16px;
  background:linear-gradient(to top,var(--bg) 70%,transparent);align-items:center}
.cardnav button{flex:1;font-family:var(--mono);font-size:13px;padding:13px 10px;
  background:var(--surface);border:1px solid var(--line);color:var(--ink-2);border-radius:8px;cursor:pointer}
.cardnav button:hover{border-color:var(--accent);color:var(--accent)}
.cardnav .pos{font-family:var(--mono);font-size:12px;color:var(--muted);white-space:nowrap}
.keyhint{font-family:var(--mono);font-size:11px;color:var(--muted);margin:0 0 18px;line-height:1.9}
.keyhint kbd{font-family:var(--mono);font-size:10.5px;background:var(--surface);
  border:1px solid var(--line);border-bottom-width:2px;border-radius:4px;padding:1px 5px;color:var(--ink-2)}
.q.active{border-color:var(--accent);box-shadow:0 0 0 2px var(--accent-soft),var(--shadow)}
.empty{color:var(--muted);font-family:var(--mono);font-size:12.5px;padding:18px 0}
.empty[hidden]{display:none}

@media (max-width:900px){
  .shell{grid-template-columns:minmax(0,1fr);gap:0;padding:0 18px 72px}
  .rail{position:static;max-height:none;padding:20px 0 0;border-bottom:1px solid var(--line)}
  .rail nav{flex-direction:row;overflow-x:auto;gap:4px;padding-bottom:12px}
  .rail a{white-space:nowrap;background:var(--surface);border:1px solid var(--line-soft)}
  .topbar{padding:9px 18px}
  .score{min-width:0}
  .score .verdict{display:none}
  input[type=search]{width:130px}
  .main{padding-top:24px}
  .qh{grid-template-columns:28px minmax(0,1fr);row-gap:6px}
  .mark{grid-column:2}
  .keyhint{display:none}
  .q{padding:16px 15px}
  .reveal{padding:13px 14px;font-size:12px}
  .rate{gap:8px}
  .rate button{flex:1;min-width:76px;padding:11px 8px;font-size:12px;text-align:center}
  .rate button.clr{flex:0 0 auto;min-width:44px;margin-left:0}
  .rate .rl{flex-basis:100%;margin:0 0 2px}
}
@media (prefers-reduced-motion:reduce){*{transition:none!important;scroll-behavior:auto!important}}
</style>
<!--SPLIT-->
<div class="topbar">
  <div class="topbar-in">
    <div class="score">
      <span class="big" id="pct">—</span>
      <span class="meter"><i class="m2" id="m2"></i><i class="m1" id="m1"></i><i class="m0" id="m0"></i></span>
      <span class="verdict" id="verdict">оцени первый вопрос</span>
      <span class="timer" id="timer" hidden>00:00</span>
    </div>
    <div class="tools">
      <input type="search" id="search" placeholder="поиск" aria-label="Поиск по вопросам">
      <button class="chip on" data-filter="all" type="button">все</button>
      <button class="chip" data-filter="todo" type="button">не оценено</button>
      <button class="chip" data-filter="weak" type="button">0 и 1</button>
      <button class="chip" data-filter="due" type="button">повторить <span id="dueN"></span></button>
      <button class="chip" id="resume" type="button">продолжить</button>
      <button class="chip" id="examBtn" type="button">экзамен</button>
      <button class="chip" id="cardsBtn" type="button">карточки</button>
      <button class="chip" id="syncBtn" type="button">синхрон</button>
      <button class="chip" id="collapse" type="button">скрыть ответы</button>
      <button class="chip" id="reset" type="button">сбросить</button>
    </div>
  </div>
</div>

<div class="shell">
  <aside class="rail">
    <p class="rail-title">Разделы</p>
    <nav>{{NAV}}</nav>
  </aside>

  <main class="main">
    <header class="masthead">
      <p class="eyebrow">Тренажёр · {{TOTAL}} вопросов</p>
      <h1>{{TITLE}}</h1>
      <div class="prose lead">{{INTRO}}</div>
    </header>
    <div class="panel" id="examPanel" hidden>
      <p class="pt">Режим экзамена</p>
      <p class="pd">Случайные вопросы, таймер, ответ открывается только после того, как ты поставил себе оценку. Так же, как на собеседовании: сначала отвечаешь, потом узнаёшь.</p>
      <div class="prow">
        <button class="chip" data-exam="10" type="button">10 вопросов · 10 мин</button>
        <button class="chip" data-exam="20" type="button">20 вопросов · 20 мин</button>
        <button class="chip" data-exam="30" type="button">30 вопросов · 30 мин</button>
        <button class="chip" data-exam="0" type="button">отмена</button>
      </div>
    </div>

    <div class="panel" id="syncPanel" hidden>
      <p class="pt">Перенос прогресса между устройствами</p>
      <p class="pd">Оценки хранятся в браузере, поэтому между ноутом и телефоном не переносятся сами. Скопируй код здесь и вставь его на другом устройстве.</p>
      <textarea id="syncBox" rows="3" spellcheck="false" aria-label="Код прогресса"></textarea>
      <div class="prow">
        <button class="chip" id="syncCopy" type="button">скопировать</button>
        <button class="chip" id="syncApply" type="button">применить вставленный</button>
        <button class="chip" id="syncClose" type="button">закрыть</button>
        <span class="pmsg" id="syncMsg"></span>
      </div>
    </div>

    <div class="panel" id="resultPanel" hidden></div>

    <p class="keyhint">С клавиатуры: <kbd>Space</kbd> показать ответ · <kbd>0</kbd> <kbd>1</kbd> <kbd>2</kbd> оценка ·
      <kbd>J</kbd> / <kbd>K</kbd> следующий и предыдущий вопрос · <kbd>/</kbd> поиск</p>
    <p class="empty" id="empty" hidden>Ничего не найдено — измени запрос или фильтр.</p>
    {{BODY}}
    <div class="cardnav" id="cardnav">
      <button type="button" id="cardPrev">← назад</button>
      <span class="pos" id="cardPos">—</span>
      <button type="button" id="cardNext">вперёд →</button>
    </div>
  </main>
</div>

<script>
(function(){
  var KEY="qa-trainer-v2", OLD="qa-trainer-v1", TOTAL={{TOTAL}};
  var GAP={"0":1,"1":3,"2":14};                 // дней до повторения
  var today=function(){return Math.floor(Date.now()/864e5)};

  // ── хранилище: {v:{n:"0|1|2"}, d:{n:день_повторения}} ──
  var data={v:{},d:{}};
  try{
    var raw=localStorage.getItem(KEY);
    if(raw){ data=JSON.parse(raw); data.v=data.v||{}; data.d=data.d||{}; }
    else{
      var old=localStorage.getItem(OLD);
      if(old){ data.v=JSON.parse(old)||{}; data.d={}; }
    }
  }catch(e){ data={v:{},d:{}} }
  function save(){ try{localStorage.setItem(KEY,JSON.stringify(data))}catch(e){} }

  var cards=Array.prototype.slice.call(document.querySelectorAll(".q"));
  var LABEL={"0":"0 — не знаю","1":"1 — плыл","2":"2 — уверенно"};
  var el=function(id){return document.getElementById(id)};

  var exam=null;            // {set:Set, ends:ms, tick:id}
  var cardsMode=false;
  var filter="all", query="", activeIdx=-1;

  // ── отрисовка одной карточки ──
  function paint(card){
    var n=card.getAttribute("data-q"), v=data.v[n];
    var mark=card.querySelector("[data-mark]");
    var rev=card.querySelector(".reveal");
    if(v===undefined){ card.removeAttribute("data-v"); mark.textContent=""; }
    else { card.setAttribute("data-v",v); mark.textContent=LABEL[v]; }
    if(rev){
      var locked = exam && v===undefined;
      rev.disabled=!!locked;
      rev.textContent = locked ? "Сначала поставь оценку" : "Показать ответ";
    }
  }

  function setVal(card,v){
    var n=card.getAttribute("data-q");
    if(v===null){ delete data.v[n]; delete data.d[n]; }
    else { data.v[n]=v; data.d[n]=today()+GAP[v]; }
    save(); paint(card); recount();
  }

  // ── счёт ──
  function verdictFor(p){
    if(p<40) return "junior / вход в DevOps — база есть, системы нет";
    if(p<60) return "junior+ / middle-минус — срезают на глубине";
    if(p<80) return "middle — целевой уровень, можно торговаться";
    return "middle+ / senior — вилка выше рынка";
  }
  function dueCount(){
    var t=today(), k=0;
    for(var n in data.d){ if(data.d.hasOwnProperty(n) && data.d[n]<=t) k++; }
    return k;
  }
  function recount(){
    var c={0:0,1:0,2:0}, rated=0;
    for(var k in data.v){ if(data.v.hasOwnProperty(k)){ c[data.v[k]]++; rated++; } }
    var pct=TOTAL?Math.round(c[2]/TOTAL*100):0;
    el("pct").textContent=rated?pct+"%":"—";
    el("m2").style.width=(c[2]/TOTAL*100)+"%";
    el("m1").style.width=(c[1]/TOTAL*100)+"%";
    el("m0").style.width=(c[0]/TOTAL*100)+"%";
    el("verdict").textContent=rated?(verdictFor(pct)+" · оценено "+rated+" из "+TOTAL):"оцени первый вопрос";
    var d=dueCount(); el("dueN").textContent=d?("· "+d):"";

    var per={};
    cards.forEach(function(card){
      var sec=card.getAttribute("data-sec"), n=card.getAttribute("data-q");
      per[sec]=per[sec]||{two:0,tot:0}; per[sec].tot++;
      if(data.v[n]==="2") per[sec].two++;
    });
    Object.keys(per).forEach(function(sec){
      var x=per[sec];
      var a=document.querySelector('.nsc[data-sec="'+sec+'"]'); if(a) a.textContent=x.two+"/"+x.tot;
      var f=document.querySelector('[data-secfill="'+sec+'"]'); if(f) f.style.width=(x.two/x.tot*100)+"%";
      var l=document.querySelector('[data-seclabel="'+sec+'"]'); if(l) l.textContent=x.two+" / "+x.tot;
    });
  }

  // ── фильтры ──
  function visibleCards(){ return cards.filter(function(c){return !c.classList.contains("hide")}) }

  function applyFilter(){
    var t=today(), shown=0;
    cards.forEach(function(card){
      var n=card.getAttribute("data-q"), v=data.v[n], ok=true;
      if(exam) ok=exam.set.has(n);
      else if(filter==="todo") ok=(v===undefined);
      else if(filter==="weak") ok=(v==="0"||v==="1");
      else if(filter==="due") ok=(data.d[n]!==undefined && data.d[n]<=t);
      if(ok&&query) ok=card.getAttribute("data-text").indexOf(query)>-1;
      card.classList.toggle("hide",!ok);
      if(ok) shown++;
    });
    var em=el("empty");
    em.hidden=(shown>0);
    if(!em.hidden){
      em.textContent = (filter==="due" && !query)
        ? "Сегодня повторять нечего — очередь пополнится, когда подойдёт срок: ноль через день, единица через три, двойка через две недели."
        : (filter==="todo" && !query)
          ? "Оценены все вопросы. Дальше — фильтр «повторить» или режим экзамена."
          : "Ничего не найдено — измени запрос или фильтр.";
    }
    document.querySelectorAll("section[data-sec]").forEach(function(sec){
      var qs=sec.querySelectorAll(".q");
      if(!qs.length){ sec.style.display=(filter==="all"&&!query&&!exam&&!cardsMode)?"":"none"; return; }
      var any=Array.prototype.slice.call(qs).some(function(c){return !c.classList.contains("hide")});
      sec.style.display=any?"":"none";
    });
    if(cardsMode) setActive(activeIdx<0?0:Math.min(activeIdx,visibleCards().length-1),false);
    updateCardNav();
  }

  // ── активная карточка ──
  function setActive(i,scroll){
    var vis=visibleCards();
    if(!vis.length){ activeIdx=-1; updateCardNav(); return; }
    if(i<0) i=0; if(i>=vis.length) i=vis.length-1;
    cards.forEach(function(c){c.classList.remove("active")});
    vis[i].classList.add("active"); activeIdx=i;
    if(scroll!==false) vis[i].scrollIntoView({block:cardsMode?"start":"center",behavior:"smooth"});
    updateCardNav();
  }
  function activeCard(){ var vis=visibleCards(); return (activeIdx>=0&&activeIdx<vis.length)?vis[activeIdx]:null }
  function updateCardNav(){
    if(!cardsMode) return;
    var vis=visibleCards();
    el("cardPos").textContent=vis.length?((activeIdx+1)+" / "+vis.length):"—";
  }

  // ── клики ──
  document.addEventListener("click",function(e){
    var r=e.target.closest(".reveal");
    if(r&&!r.disabled){
      document.querySelector('[data-ans="'+r.getAttribute("data-reveal")+'"]').hidden=false;
      r.hidden=true; return;
    }
    var b=e.target.closest(".rate button");
    if(b){
      var card=b.closest(".q"), v=b.getAttribute("data-v");
      setVal(card, v==="-"?null:v);
      var wasIdx=visibleCards().indexOf(card);
      if(!exam&&!cardsMode&&(filter==="todo"||filter==="weak"||filter==="due")){
        applyFilter(); setActive(Math.min(wasIdx,visibleCards().length-1),false);
      } else { applyFilter(); }
      if(exam) maybeFinish();
      return;
    }
    var c=e.target.closest(".q");
    if(c) setActive(visibleCards().indexOf(c),false);
  });

  document.querySelectorAll("[data-filter]").forEach(function(btn){
    btn.addEventListener("click",function(){
      if(exam) return;
      document.querySelectorAll("[data-filter]").forEach(function(x){x.classList.remove("on")});
      btn.classList.add("on"); filter=btn.getAttribute("data-filter"); activeIdx=-1; applyFilter();
    });
  });
  el("search").addEventListener("input",function(e){ query=e.target.value.trim().toLowerCase(); applyFilter(); });

  el("resume").addEventListener("click",function(){
    var vis=visibleCards();
    for(var i=0;i<vis.length;i++){ if(data.v[vis[i].getAttribute("data-q")]===undefined){ setActive(i); return; } }
    setActive(0);
  });

  el("collapse").addEventListener("click",function(){
    document.querySelectorAll("[data-ans]").forEach(function(a){a.hidden=true});
    document.querySelectorAll(".reveal").forEach(function(x){x.hidden=false});
    cards.forEach(paint);
    window.scrollTo({top:0,behavior:"smooth"});
  });

  el("reset").addEventListener("click",function(){
    if(!confirm("Сбросить все оценки?")) return;
    data={v:{},d:{}}; save(); cards.forEach(paint); recount(); applyFilter();
  });

  // ── карточный режим ──
  el("cardsBtn").addEventListener("click",function(){
    cardsMode=!cardsMode;
    document.body.classList.toggle("cards",cardsMode);
    el("cardsBtn").classList.toggle("on",cardsMode);
    applyFilter(); setActive(cardsMode?0:activeIdx,cardsMode);
  });
  el("cardPrev").addEventListener("click",function(){ setActive(activeIdx-1) });
  el("cardNext").addEventListener("click",function(){ setActive(activeIdx+1) });

  var tx=0;
  document.addEventListener("touchstart",function(e){ tx=e.changedTouches[0].clientX },{passive:true});
  document.addEventListener("touchend",function(e){
    if(!cardsMode) return;
    var dx=e.changedTouches[0].clientX-tx;
    if(Math.abs(dx)>70) setActive(activeIdx+(dx<0?1:-1));
  },{passive:true});

  // ── экзамен ──
  el("examBtn").addEventListener("click",function(){
    if(exam){ finishExam(true); return; }
    el("examPanel").hidden=!el("examPanel").hidden;
    el("syncPanel").hidden=true;
  });
  document.querySelectorAll("[data-exam]").forEach(function(btn){
    btn.addEventListener("click",function(){
      var n=parseInt(btn.getAttribute("data-exam"),10);
      el("examPanel").hidden=true;
      if(n>0) startExam(n);
    });
  });

  function startExam(n){
    var pool=cards.slice();
    for(var i=pool.length-1;i>0;i--){ var j=Math.floor(Math.random()*(i+1)); var t=pool[i]; pool[i]=pool[j]; pool[j]=t; }
    var chosen=pool.slice(0,Math.min(n,pool.length));
    exam={set:new Set(chosen.map(function(c){return c.getAttribute("data-q")})), total:chosen.length,
          ends:Date.now()+n*60000, tick:null, start:{}};
    chosen.forEach(function(c){ var q=c.getAttribute("data-q"); exam.start[q]=data.v[q]; delete data.v[q]; });
    save();
    document.querySelectorAll("[data-ans]").forEach(function(a){a.hidden=true});
    document.querySelectorAll(".reveal").forEach(function(x){x.hidden=false});
    el("examBtn").textContent="завершить"; el("examBtn").classList.add("on");
    el("resultPanel").hidden=true;
    query=""; el("search").value="";
    cards.forEach(paint); recount(); applyFilter(); setActive(0);
    exam.tick=setInterval(tickTimer,1000); tickTimer();
  }

  function tickTimer(){
    if(!exam) return;
    var left=Math.max(0,Math.round((exam.ends-Date.now())/1000));
    var t=el("timer"); t.hidden=false;
    t.textContent=String(Math.floor(left/60)).padStart(2,"0")+":"+String(left%60).padStart(2,"0");
    t.classList.toggle("low",left<=60);
    if(left<=0) finishExam(false);
  }

  function maybeFinish(){
    if(!exam) return;
    var done=0;
    exam.set.forEach(function(q){ if(data.v[q]!==undefined) done++; });
    if(done>=exam.total) finishExam(false);
  }

  function finishExam(cancelled){
    if(!exam) return;
    clearInterval(exam.tick);
    var ids=Array.from(exam.set), c={0:0,1:0,2:0}, unrated=0;
    ids.forEach(function(q){ var v=data.v[q]; if(v===undefined) unrated++; else c[v]++; });
    var answered=ids.length-unrated;
    var pct=answered?Math.round(c[2]/ids.length*100):0;
    exam=null;
    el("timer").hidden=true;
    el("examBtn").textContent="экзамен"; el("examBtn").classList.remove("on");

    if(!cancelled){
      var p=el("resultPanel");
      p.innerHTML='<p class="pt">Результат экзамена</p>'
        +'<p><span class="big2">'+pct+'%</span> уверенных ответов из '+ids.length+' вопросов</p>'
        +'<p class="pd">'+verdictFor(pct)+'. Уверенно: '+c["2"]+' · плыл: '+c["1"]+' · не знаю: '+c["0"]
        +(unrated?' · не дошёл: '+unrated:'')+'.</p>'
        +'<p class="pd">Всё, что ниже двойки, попало в очередь повторения — фильтр «повторить».</p>'
        +'<div class="prow"><button class="chip" id="resClose" type="button">закрыть</button>'
        +'<button class="chip" data-filter-jump="weak" type="button">показать провалы</button></div>';
      p.hidden=false;
      el("resClose").addEventListener("click",function(){p.hidden=true});
      p.querySelector("[data-filter-jump]").addEventListener("click",function(){
        p.hidden=true;
        var w=document.querySelector('[data-filter="weak"]'); if(w) w.click();
      });
      window.scrollTo({top:0,behavior:"smooth"});
    }
    cards.forEach(paint); recount(); applyFilter();
  }

  // ── перенос прогресса ──
  el("syncBtn").addEventListener("click",function(){
    var p=el("syncPanel"); p.hidden=!p.hidden; el("examPanel").hidden=true;
    if(!p.hidden){ el("syncBox").value=encodeState(); el("syncMsg").textContent=""; }
  });
  el("syncClose").addEventListener("click",function(){ el("syncPanel").hidden=true });

  function encodeState(){
    try{ return "QA2:"+btoa(unescape(encodeURIComponent(JSON.stringify(data)))); }
    catch(e){ return "" }
  }
  function decodeState(str){
    str=(str||"").trim();
    if(str.indexOf("QA2:")===0) str=str.slice(4);
    var obj=JSON.parse(decodeURIComponent(escape(atob(str))));
    if(!obj||typeof obj!=="object"||!obj.v) throw new Error("формат");
    return obj;
  }
  el("syncCopy").addEventListener("click",function(){
    var box=el("syncBox"); box.value=encodeState(); box.select();
    var done=function(){ el("syncMsg").textContent="скопировано" };
    if(navigator.clipboard) navigator.clipboard.writeText(box.value).then(done,function(){ document.execCommand("copy"); done(); });
    else { document.execCommand("copy"); done(); }
  });
  el("syncApply").addEventListener("click",function(){
    try{
      var obj=decodeState(el("syncBox").value);
      var n=Object.keys(obj.v).length;
      data={v:obj.v||{},d:obj.d||{}}; save();
      cards.forEach(paint); recount(); applyFilter();
      el("syncMsg").textContent="применено: "+n+" оценок";
    }catch(err){ el("syncMsg").textContent="не разобрал код"; }
  });

  // ── клавиатура ──
  document.addEventListener("keydown",function(e){
    var sb=el("search");
    if(e.key==="/"&&document.activeElement!==sb){ e.preventDefault(); sb.focus(); return; }
    if(document.activeElement===sb){ if(e.key==="Escape") sb.blur(); return; }
    if(document.activeElement===el("syncBox")) return;
    if(e.metaKey||e.ctrlKey||e.altKey) return;

    var k=e.key.toLowerCase();
    if(k==="j"||e.key==="ArrowRight"){ e.preventDefault(); setActive(activeIdx<0?0:activeIdx+1); return; }
    if(k==="k"||e.key==="ArrowLeft"){ e.preventDefault(); setActive(activeIdx<0?0:activeIdx-1); return; }

    var card=activeCard(); if(!card) return;
    if(e.key===" "||e.key==="Enter"){
      var btn=card.querySelector(".reveal");
      if(btn&&!btn.hidden&&!btn.disabled){ e.preventDefault(); btn.click(); }
      return;
    }
    if(k==="0"||k==="1"||k==="2"){
      e.preventDefault();
      var idx=visibleCards().indexOf(card);
      setVal(card,k);
      if(!exam&&!cardsMode&&(filter==="todo"||filter==="weak"||filter==="due")){
        applyFilter(); setActive(Math.min(idx,visibleCards().length-1));
      } else { applyFilter(); setActive(idx+1); }
      if(exam) maybeFinish();
      return;
    }
    if(k==="x"){ e.preventDefault(); setVal(card,null); applyFilter(); }
  });

  cards.forEach(paint); recount(); applyFilter();
})();
</script>
"""


DOC_HEAD = """<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="Тренажёр для подготовки к собеседованию DevOps/SRE: 151 вопрос с ответами, объяснениями и самооценкой. Linux, Kubernetes, Docker, Terraform, Ansible, CI/CD, мониторинг и SRE.">
<meta name="theme-color" content="#EFF1F3" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#0F1319" media="(prefers-color-scheme: dark)">
<link rel="manifest" href="manifest.webmanifest">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>&#9096;</text></svg>">
"""


def wrap_standalone(fragment):
    """Полный HTML-документ для отдачи с GitHub Pages."""
    head, body = fragment.split("<!--SPLIT-->", 1)
    return DOC_HEAD + head + SITE_NAV_CSS + "</head>\n<body>\n" + SITE_NAV + body + "\n</body>\n</html>\n"


def main():
    fragment_mode = "--fragment" in sys.argv
    out_path = OUT
    for i, a in enumerate(sys.argv):
        if a == "-o" and i + 1 < len(sys.argv):
            out_path = sys.argv[i + 1]

    with open(SRC, encoding="utf-8") as fh:
        text = fh.read()
    doc_title, intro_blocks, sections = parse(text)
    out = build(doc_title, intro_blocks, sections)
    if fragment_mode:
        out = out.replace("<!--SPLIT-->\n", "")
    else:
        out = wrap_standalone(out)
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(out)
    OUT_USED.append(out_path)
    nq = sum(1 for s in sections for it in s["items"] if it["num"])
    print("%s: sections=%d questions=%d chars=%d" % (out_path, len(sections), nq, len(out)))


if __name__ == "__main__":
    main()
