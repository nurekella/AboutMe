#!/usr/bin/env python3
"""Собирает интерактивный тренажёр (HTML) из INTERVIEW_QA.md."""

import html
import re
import sys

SRC = "INTERVIEW_QA.md"
OUT = "site/qa-trainer.html"

MARKERS = ("Что проверяют", "Глубже", "Типичная ошибка", "Типичные ошибки")
ANSWER_STARTS = ("**Ответ", "**Как отвечать", "**Структура", "**Хорошие вопросы")


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
}
@media (prefers-reduced-motion:reduce){*{transition:none!important;scroll-behavior:auto!important}}
</style>

<div class="topbar">
  <div class="topbar-in">
    <div class="score">
      <span class="big" id="pct">—</span>
      <span class="meter"><i class="m2" id="m2"></i><i class="m1" id="m1"></i><i class="m0" id="m0"></i></span>
      <span class="verdict" id="verdict">оцени первый вопрос</span>
    </div>
    <div class="tools">
      <input type="search" id="search" placeholder="поиск по вопросам" aria-label="Поиск по вопросам">
      <button class="chip on" data-filter="all" type="button">все</button>
      <button class="chip" data-filter="todo" type="button">не оценено</button>
      <button class="chip" data-filter="weak" type="button">0 и 1</button>
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
    <p class="empty" id="empty" hidden>Ничего не найдено — измени запрос или фильтр.</p>
    {{BODY}}
  </main>
</div>

<script>
(function(){
  var KEY="qa-trainer-v1", TOTAL={{TOTAL}};
  var state={};
  try{state=JSON.parse(localStorage.getItem(KEY))||{}}catch(e){state={}}
  function save(){try{localStorage.setItem(KEY,JSON.stringify(state))}catch(e){}}

  var cards=[].slice.call(document.querySelectorAll(".q"));
  var LABEL={"0":"0 — не знаю","1":"1 — плыл","2":"2 — уверенно"};

  function paint(card){
    var n=card.getAttribute("data-q"), v=state[n];
    var mark=card.querySelector("[data-mark]");
    if(v===undefined){card.removeAttribute("data-v");mark.textContent=""}
    else{card.setAttribute("data-v",v);mark.textContent=LABEL[v]}
  }

  function verdictFor(p){
    if(p<40) return "junior / вход в DevOps — база есть, системы нет";
    if(p<60) return "junior+ / middle-минус — срезают на глубине";
    if(p<80) return "middle — целевой уровень, можно торговаться";
    return "middle+ / senior — вилка выше рынка";
  }

  function recount(){
    var c={0:0,1:0,2:0}, rated=0;
    for(var k in state){if(state.hasOwnProperty(k)){c[state[k]]++;rated++}}
    var pct=TOTAL?Math.round(c[2]/TOTAL*100):0;
    document.getElementById("pct").textContent=rated?pct+"%":"—";
    document.getElementById("m2").style.width=(c[2]/TOTAL*100)+"%";
    document.getElementById("m1").style.width=(c[1]/TOTAL*100)+"%";
    document.getElementById("m0").style.width=(c[0]/TOTAL*100)+"%";
    document.getElementById("verdict").textContent=
      rated?(verdictFor(pct)+" · оценено "+rated+" из "+TOTAL):"оцени первый вопрос";

    var per={};
    cards.forEach(function(card){
      var s=card.getAttribute("data-sec"), n=card.getAttribute("data-q");
      per[s]=per[s]||{two:0,tot:0};
      per[s].tot++;
      if(state[n]==="2"||state[n]===2) per[s].two++;
    });
    Object.keys(per).forEach(function(s){
      var d=per[s];
      var nsc=document.querySelector('.nsc[data-sec="'+s+'"]');
      if(nsc) nsc.textContent=d.two+"/"+d.tot;
      var fill=document.querySelector('[data-secfill="'+s+'"]');
      if(fill) fill.style.width=(d.two/d.tot*100)+"%";
      var lab=document.querySelector('[data-seclabel="'+s+'"]');
      if(lab) lab.textContent=d.two+" / "+d.tot;
    });
  }

  document.addEventListener("click",function(e){
    var r=e.target.closest(".reveal");
    if(r){
      var n=r.getAttribute("data-reveal");
      document.querySelector('[data-ans="'+n+'"]').hidden=false;
      r.hidden=true;
      return;
    }
    var b=e.target.closest(".rate button");
    if(b){
      var card=b.closest(".q"), n2=card.getAttribute("data-q"), v=b.getAttribute("data-v");
      if(v==="-") delete state[n2]; else state[n2]=v;
      save(); paint(card); recount(); applyFilter();
      return;
    }
  });

  var filter="all", query="";
  document.querySelectorAll("[data-filter]").forEach(function(btn){
    btn.addEventListener("click",function(){
      document.querySelectorAll("[data-filter]").forEach(function(x){x.classList.remove("on")});
      btn.classList.add("on"); filter=btn.getAttribute("data-filter"); applyFilter();
    });
  });
  document.getElementById("search").addEventListener("input",function(e){
    query=e.target.value.trim().toLowerCase(); applyFilter();
  });

  function applyFilter(){
    var shown=0;
    cards.forEach(function(card){
      var n=card.getAttribute("data-q"), v=state[n], ok=true;
      if(filter==="todo") ok=(v===undefined);
      else if(filter==="weak") ok=(v==="0"||v==="1");
      if(ok&&query) ok=card.getAttribute("data-text").indexOf(query)>-1;
      card.classList.toggle("hide",!ok);
      if(ok) shown++;
    });
    document.getElementById("empty").hidden=(shown>0);
    document.querySelectorAll("section[data-sec]").forEach(function(sec){
      var qs=sec.querySelectorAll(".q");
      if(!qs.length) { sec.style.display=(filter==="all"&&!query)?"":"none"; return; }
      var any=[].slice.call(qs).some(function(c){return !c.classList.contains("hide")});
      sec.style.display=any?"":"none";
    });
  }

  document.getElementById("collapse").addEventListener("click",function(){
    document.querySelectorAll("[data-ans]").forEach(function(a){a.hidden=true});
    document.querySelectorAll(".reveal").forEach(function(r){r.hidden=false});
    window.scrollTo({top:0,behavior:"smooth"});
  });

  document.getElementById("reset").addEventListener("click",function(){
    if(!confirm("Сбросить все оценки?")) return;
    state={}; save();
    cards.forEach(paint); recount(); applyFilter();
  });

  cards.forEach(paint); recount(); applyFilter();
})();
</script>
"""


def main():
    with open(SRC, encoding="utf-8") as fh:
        text = fh.read()
    doc_title, intro_blocks, sections = parse(text)
    out = build(doc_title, intro_blocks, sections)
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(out)
    nq = sum(1 for s in sections for it in s["items"] if it["num"])
    print("sections=%d questions=%d bytes=%d" % (len(sections), nq, len(out)))
    if nq != 151:
        print("WARNING: ожидалось 151 вопрос", file=sys.stderr)


if __name__ == "__main__":
    main()
