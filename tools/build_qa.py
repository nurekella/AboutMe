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

# Грейд рендерится не как callout, а как значок в шапке вопроса и атрибут для фильтра.
GRADES = ("junior", "middle", "senior")


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
            bs = blocks(body)
            grade = None
            for bi, (kind, payload) in enumerate(bs):
                if kind == "p" and isinstance(payload, str) and payload.startswith("`Грейд`"):
                    g = payload[len("`Грейд`"):].strip().lower()
                    if g in GRADES:
                        grade = g
                        bs = bs[:bi] + bs[bi + 1:]
                    break
            cur["items"].append({
                "num": int(m.group(1)) if m else None,
                "title": m.group(2) if m else heading,
                "grade": grade,
                "blocks": bs,
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
                grade = it.get("grade") or "middle"
                body.append(
                    '<article class="q" id="%s" data-q="%d" data-sec="%d" data-grade="%s" '
                    'data-text="%s">' % (
                        qid, it["num"], si, grade,
                        html.escape(("%d %s" % (it["num"], it["title"])).lower(), quote=True)))
                body.append('<header class="qh"><span class="qn mono">%02d</span>'
                            '<h3>%s</h3><span class="grade mono" data-gr="%s">%s</span>'
                            '<span class="mark mono" data-mark="%d"></span></header>'
                            % (it["num"], inline(it["title"]), grade, grade, it["num"]))
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
                body.append(EXTRAS % {"n": it["num"]})
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
    tpl = tpl.replace("{{SCRIPT}}", SCRIPT)
    tpl = tpl.replace("{{TOTAL}}", str(total_q))
    return tpl


SCRIPT = r"""<script>
(function(){
  var KEY="qa-study-v3", OLD2="qa-trainer-v2", OLD1="qa-trainer-v1", TOTAL={{TOTAL}};
  var GAP={"0":1,"1":3,"2":14};
  var today=function(){return Math.floor(Date.now()/864e5)};
  var el=function(id){return document.getElementById(id)};

  // ── хранилище ──
  var data={v:{},d:{},notes:{},custom:[],days:{},diary:[]};
  function migrate(){
    try{
      var raw=localStorage.getItem(KEY);
      if(raw){ var o=JSON.parse(raw)||{};
        data={v:o.v||{},d:o.d||{},notes:o.notes||{},custom:o.custom||[],days:o.days||{},diary:o.diary||[]};
        return; }
      var v2=localStorage.getItem(OLD2);
      if(v2){ var b=JSON.parse(v2)||{}; data.v=b.v||{}; data.d=b.d||{}; return; }
      var v1=localStorage.getItem(OLD1);
      if(v1){ data.v=JSON.parse(v1)||{}; }
    }catch(e){}
  }
  migrate();
  function save(){ try{localStorage.setItem(KEY,JSON.stringify(data))}catch(e){} }

  var cards=[];
  var LABEL={"0":"0 — не знаю","1":"1 — плыл","2":"2 — уверенно"};
  var exam=null, cardsMode=false, filter="all", gfilter="all", query="", activeIdx=-1;
  var GRADES=["junior","middle","senior"], GDONE=0.7;

  // ── свои вопросы ──
  var EXTRA_TPL=function(n){return '<div class="extras">'
    +'<button class="xbtn" type="button" data-note="'+n+'">заметка</button>'
    +'<button class="xbtn" type="button" data-rec="'+n+'">записать ответ</button>'
    +'<span class="recinfo mono" data-recinfo="'+n+'"></span></div>'
    +'<div class="notewrap" data-notewrap="'+n+'" hidden><textarea data-noteta="'+n+'" rows="3" '
    +'placeholder="Своими словами"></textarea></div>'
    +'<div class="recwrap" data-recwrap="'+n+'" hidden></div>'};

  function esc(t){ return String(t||"").replace(/[&<>"]/g,function(c){
    return {"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c] }) }

  function renderCustom(){
    var box=el("mineList"); if(!box) return;
    box.innerHTML="";
    data.custom.forEach(function(item){
      var n=item.id;
      var d=document.createElement("article");
      d.className="q"; d.id="q"+n;
      d.setAttribute("data-q",n); d.setAttribute("data-sec","mine");
      d.setAttribute("data-text",(item.q||"").toLowerCase());
      d.innerHTML='<header class="qh"><span class="qn mono">'+esc(n)+'</span><h3>'+esc(item.q)+'</h3>'
        +'<span class="mark mono" data-mark="'+n+'"></span></header>'
        +'<button class="reveal" type="button" data-reveal="'+n+'">Показать ответ</button>'
        +'<div class="prose ans" data-ans="'+n+'" hidden><p>'+esc(item.a).replace(/\n/g,"<br>")+'</p></div>'
        +'<div class="rate" data-rate="'+n+'"><span class="rl mono">Оценка</span>'
        +'<button type="button" data-v="0">0 — не знаю</button>'
        +'<button type="button" data-v="1">1 — плыл</button>'
        +'<button type="button" data-v="2">2 — уверенно</button>'
        +'<button type="button" data-v="-" class="clr">×</button>'
        +'<button type="button" data-del="'+n+'" class="clr">удалить</button></div>'
        +EXTRA_TPL(n);
      box.appendChild(d);
    });
    el("mine").hidden=data.custom.length===0;
    if(el("mineCount")) el("mineCount").textContent=data.custom.length+" шт";
    collect();
  }

  function collect(){
    cards=Array.prototype.slice.call(document.querySelectorAll(".q"));
    cards.forEach(paint);
  }

  // ── кнопка «показать/скрыть ответ» ──
  function revealState(card){
    var n=card.getAttribute("data-q");
    var rev=card.querySelector(".reveal");
    var ans=document.querySelector('[data-ans="'+n+'"]');
    if(!rev||!ans) return;
    var open=!ans.hidden;
    var locked = exam && data.v[n]===undefined && !open;
    rev.disabled=!!locked;
    rev.classList.toggle("open",open);
    rev.textContent = locked ? "Сначала поставь оценку"
                    : (open ? "Скрыть ответ" : "Показать ответ");
  }

  // ── карточка ──
  function paint(card){
    var n=card.getAttribute("data-q"), v=data.v[n];
    var mark=card.querySelector("[data-mark]");
    var rev=card.querySelector(".reveal");
    if(v===undefined){ card.removeAttribute("data-v"); if(mark) mark.textContent=""; }
    else { card.setAttribute("data-v",v); if(mark) mark.textContent=LABEL[v]; }
    revealState(card);
    card.classList.toggle("hasnote", !!(data.notes[n]&&data.notes[n].trim()));
    var ta=card.querySelector("[data-noteta]");
    if(ta && ta.value!==(data.notes[n]||"")) ta.value=data.notes[n]||"";
  }

  function bumpDay(){
    var t=String(today());
    data.days[t]=(data.days[t]||0)+1;
  }

  function setVal(card,v){
    var n=card.getAttribute("data-q");
    if(v===null){ delete data.v[n]; delete data.d[n]; }
    else { data.v[n]=v; data.d[n]=today()+GAP[v]; bumpDay(); }
    save(); paint(card); recount();
  }

  // ── счёт ──
  // Вердикт в шапке считается по грейдам, а не по общему проценту:
  // 60% с провалом на junior хуже, чем 45% с закрытым junior.
  function verdictFor(){
    var g=gradeStats(), closed=[];
    for(var i=0;i<GRADES.length;i++){
      var x=g[GRADES[i]];
      if(x.tot && x.two/x.tot>=GDONE) closed.push(GRADES[i]); else break;
    }
    if(!closed.length) return "junior не закрыт — начни с него";
    if(closed.length===1) return "junior закрыт · идёшь по middle";
    if(closed.length===2) return "junior и middle закрыты · идёшь по senior";
    return "все три грейда закрыты · вилка выше рынка";
  }
  // Оценка одного прогона экзамена — здесь общий процент как раз уместен.
  function examBand(p){
    if(p<40) return "Провал: больше половины вопросов не закрыто.";
    if(p<60) return "Слабо: на таком результате срезают на глубине.";
    if(p<80) return "Норма для middle. Разбери всё, что ниже двойки.";
    return "Сильно. На собеседовании такой прогон даёт торг по вилке.";
  }
  function dueCount(){ var t=today(),k=0; for(var n in data.d){ if(data.d[n]<=t) k++ } return k }

  function recount(){
    var total=TOTAL+data.custom.length;
    var c={0:0,1:0,2:0}, rated=0;
    for(var k in data.v){ if(data.v.hasOwnProperty(k)){ c[data.v[k]]++; rated++ } }
    var pct=total?Math.round(c[2]/total*100):0;
    el("pct").textContent=rated?pct+"%":"—";
    el("m2").style.width=(c[2]/total*100)+"%";
    el("m1").style.width=(c[1]/total*100)+"%";
    el("m0").style.width=(c[0]/total*100)+"%";
    el("verdict").textContent=rated?(verdictFor()+" · оценено "+rated+" из "+total):"оцени первый вопрос";
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
    recountGrades();
  }

  // ── счёт по грейдам ──
  function gradeStats(){
    var g={};
    GRADES.forEach(function(k){ g[k]={two:0,rated:0,tot:0} });
    cards.forEach(function(card){
      var k=card.getAttribute("data-grade"); if(!g[k]) return;
      var v=data.v[card.getAttribute("data-q")];
      g[k].tot++;
      if(v!==undefined) g[k].rated++;
      if(v==="2") g[k].two++;
    });
    return g;
  }

  function recountGrades(){
    if(!el("gradeBox")) return;
    var g=gradeStats(), current=null;
    GRADES.forEach(function(k){
      var x=g[k], r=x.tot?x.two/x.tot:0, done=r>=GDONE;
      var lb=document.querySelector('[data-glabel="'+k+'"]');
      if(lb) lb.textContent=x.two+" / "+x.tot+" · "+Math.round(r*100)+"%";
      var f=document.querySelector('[data-gfill="'+k+'"]'); if(f) f.style.width=(r*100)+"%";
      var card=document.querySelector('[data-gcard="'+k+'"]');
      if(card) card.classList.toggle("done",done);
      var st=document.querySelector('[data-gstate="'+k+'"]');
      if(st){
        st.textContent = x.rated===0 ? "не начат — "+x.tot+" вопросов"
          : done ? "закрыт: двоек "+Math.round(r*100)+"%"
          : "осталось до 70%: "+Math.max(0,Math.ceil(x.tot*GDONE)-x.two)+" двоек"
            +", неоценённых "+(x.tot-x.rated);
      }
      if(!done && current===null) current=k;
    });
    GRADES.forEach(function(k){
      var card=document.querySelector('[data-gcard="'+k+'"]');
      if(card) card.classList.toggle("now",k===current);
    });
    var v=el("gverdict"); if(!v) return;
    var anyRated=GRADES.some(function(k){return g[k].rated>0});
    if(!anyRated){
      v.textContent="Грейд закрыт, когда двоек в нём 70% и больше. Начни с junior — на нём режут чаще, чем на Kubernetes.";
    } else if(current===null){
      v.textContent="Закрыты все три грейда. Дальше растёт не список вопросов, а масштаб задач — иди на собеседования и торгуйся.";
    } else if(current==="junior"){
      v.textContent="Идёшь по junior. Пока он не закрыт, глубина по Kubernetes не спасёт: провал на базе выглядит хуже незнания сложного.";
    } else if(current==="middle"){
      v.textContent="Junior закрыт, идёшь по middle. Это целевой уровень вакансий — держи фокус здесь, senior не трогай.";
    } else {
      v.textContent="Junior и middle закрыты, идёшь по senior. Здесь спрашивают не команды, а решения: деньги, риски, люди, отказоустойчивость.";
    }
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
      if(ok&&gfilter!=="all"&&!exam) ok=(card.getAttribute("data-grade")===gfilter);
      if(ok&&query) ok=card.getAttribute("data-text").indexOf(query)>-1;
      card.classList.toggle("hide",!ok);
      if(ok) shown++;
    });
    var em=el("empty");
    em.hidden=(shown>0);
    if(!em.hidden){
      em.textContent = (gfilter!=="all"&&filter==="due"&&!query)
        ? "В грейде "+gfilter+" сегодня повторять нечего."
        : (gfilter!=="all"&&filter==="todo"&&!query)
        ? "Грейд "+gfilter+" оценён целиком. Переключись на следующий."
        : (filter==="due"&&!query)
        ? "Сегодня повторять нечего — очередь пополнится, когда подойдёт срок: ноль через день, единица через три, двойка через две недели."
        : (filter==="todo"&&!query)
          ? "Оценены все вопросы. Дальше — фильтр «повторить» или режим экзамена."
          : "Ничего не найдено — измени запрос или фильтр.";
    }
    document.querySelectorAll("section[data-sec]").forEach(function(sec){
      var qs=sec.querySelectorAll(".q");
      if(!qs.length){ sec.style.display=(filter==="all"&&gfilter==="all"&&!query&&!exam&&!cardsMode)?"":"none"; return; }
      if(sec.id==="mine"&&!data.custom.length){ sec.hidden=true; return; }
      sec.hidden=false;
      var any=Array.prototype.slice.call(qs).some(function(c){return !c.classList.contains("hide")});
      sec.style.display=any?"":"none";
    });
    if(cardsMode) setActive(activeIdx<0?0:Math.min(activeIdx,visibleCards().length-1),false);
    updateCardNav();
  }

  function setActive(i,scroll){
    var vis=visibleCards();
    if(!vis.length){ activeIdx=-1; updateCardNav(); return }
    if(i<0) i=0; if(i>=vis.length) i=vis.length-1;
    cards.forEach(function(c){c.classList.remove("active")});
    vis[i].classList.add("active"); activeIdx=i;
    if(scroll!==false) vis[i].scrollIntoView({block:cardsMode?"start":"center",behavior:"smooth"});
    updateCardNav();
  }
  function activeCard(){ var v=visibleCards(); return (activeIdx>=0&&activeIdx<v.length)?v[activeIdx]:null }
  function updateCardNav(){
    if(!cardsMode) return;
    var v=visibleCards();
    el("cardPos").textContent=v.length?((activeIdx+1)+" / "+v.length):"—";
  }

  // ── запись голоса ──
  var rec={mr:null,n:null,chunks:[],timer:null,left:0};
  function stopRec(){
    if(rec.mr && rec.mr.state!=="inactive") rec.mr.stop();
    clearInterval(rec.timer); rec.timer=null;
  }
  function recButton(n){ return document.querySelector('[data-rec="'+n+'"]') }
  function recInfo(n){ return document.querySelector('[data-recinfo="'+n+'"]') }

  function toggleRecord(n){
    if(rec.n===n && rec.mr && rec.mr.state==="recording"){ stopRec(); return }
    if(rec.n!==null) stopRec();
    if(!navigator.mediaDevices||!window.MediaRecorder){
      recInfo(n).textContent="браузер не умеет запись"; return;
    }
    var b0=recButton(n);
    b0.disabled=true;
    recInfo(n).textContent="запрашиваю доступ к микрофону…";
    navigator.mediaDevices.getUserMedia({audio:true}).then(function(stream){
      b0.disabled=false;
      rec.n=n; rec.chunks=[]; rec.left=60;
      rec.mr=new MediaRecorder(stream);
      rec.mr.ondataavailable=function(e){ if(e.data.size) rec.chunks.push(e.data) };
      rec.mr.onstop=function(){
        stream.getTracks().forEach(function(t){t.stop()});
        var blob=new Blob(rec.chunks,{type:rec.mr.mimeType||"audio/webm"});
        var wrap=document.querySelector('[data-recwrap="'+n+'"]');
        wrap.hidden=false;
        wrap.innerHTML='<audio controls src="'+URL.createObjectURL(blob)+'"></audio>';
        var b=recButton(n); b.classList.remove("rec"); b.textContent="записать ответ";
        recInfo(n).textContent="послушай себя: «ну», паузы, извиняющиеся формулировки";
        rec.n=null;
      };
      rec.mr.start();
      var b=recButton(n); b.classList.add("rec"); b.textContent="остановить";
      rec.timer=setInterval(function(){
        rec.left--; recInfo(n).textContent="идёт запись, "+rec.left+" с";
        if(rec.left<=0) stopRec();
      },1000);
      recInfo(n).textContent="идёт запись, 60 с";
    }).catch(function(err){
      b0.disabled=false;
      recInfo(n).textContent = (err&&err.name==="NotAllowedError")
        ? "доступ к микрофону запрещён — разреши его в настройках сайта"
        : "микрофон недоступен на этом устройстве";
    });
  }

  // ── клики ──
  document.addEventListener("click",function(e){
    var r=e.target.closest(".reveal");
    if(r&&!r.disabled){
      var ansEl=document.querySelector('[data-ans="'+r.getAttribute("data-reveal")+'"]');
      ansEl.hidden=!ansEl.hidden;
      revealState(r.closest(".q"));
      return;
    }
    var del=e.target.closest("[data-del]");
    if(del){
      var id=del.getAttribute("data-del");
      if(!confirm("Удалить свой вопрос?")) return;
      data.custom=data.custom.filter(function(x){return x.id!==id});
      delete data.v[id]; delete data.d[id]; delete data.notes[id];
      save(); renderCustom(); recount(); applyFilter(); return;
    }
    var b=e.target.closest(".rate button");
    if(b){
      var card=b.closest(".q"), v=b.getAttribute("data-v");
      var idx=visibleCards().indexOf(card);
      setVal(card, v==="-"?null:v);
      if(!exam&&!cardsMode&&(filter==="todo"||filter==="weak"||filter==="due")){
        applyFilter(); setActive(Math.min(idx,visibleCards().length-1),false);
      } else applyFilter();
      if(exam) maybeFinish();
      return;
    }
    var nb=e.target.closest("[data-note]");
    if(nb){
      var n=nb.getAttribute("data-note");
      var w=document.querySelector('[data-notewrap="'+n+'"]');
      w.hidden=!w.hidden; nb.classList.toggle("on",!w.hidden);
      if(!w.hidden) w.querySelector("textarea").focus();
      return;
    }
    var rb=e.target.closest("[data-rec]");
    if(rb){ toggleRecord(rb.getAttribute("data-rec")); return }
    var c=e.target.closest(".q");
    if(c) setActive(visibleCards().indexOf(c),false);
  });

  document.addEventListener("input",function(e){
    var ta=e.target.closest("[data-noteta]");
    if(!ta) return;
    var n=ta.getAttribute("data-noteta");
    if(ta.value.trim()) data.notes[n]=ta.value; else delete data.notes[n];
    save();
    var card=ta.closest(".q"); if(card) card.classList.toggle("hasnote",!!ta.value.trim());
  });

  document.querySelectorAll("[data-filter]").forEach(function(btn){
    btn.addEventListener("click",function(){
      if(exam) return;
      document.querySelectorAll("[data-filter]").forEach(function(x){x.classList.remove("on")});
      btn.classList.add("on"); filter=btn.getAttribute("data-filter"); activeIdx=-1; applyFilter();
    });
  });
  document.querySelectorAll("[data-grade-filter]").forEach(function(btn){
    btn.addEventListener("click",function(){
      if(exam) return;
      document.querySelectorAll("[data-grade-filter]").forEach(function(x){x.classList.remove("on")});
      btn.classList.add("on"); gfilter=btn.getAttribute("data-grade-filter");
      activeIdx=-1; applyFilter();
      document.querySelectorAll("[data-gcard]").forEach(function(c){
        c.classList.toggle("picked",gfilter!=="all"&&c.getAttribute("data-gcard")===gfilter);
      });
    });
  });
  document.querySelectorAll("[data-gcard]").forEach(function(c){
    c.addEventListener("click",function(){
      var g=c.getAttribute("data-gcard");
      var btn=document.querySelector('[data-grade-filter="'+(gfilter===g?"all":g)+'"]');
      if(btn) btn.click();
    });
  });
  el("search").addEventListener("input",function(e){ query=e.target.value.trim().toLowerCase(); applyFilter() });

  el("resume").addEventListener("click",function(){
    var vis=visibleCards();
    for(var i=0;i<vis.length;i++){ if(data.v[vis[i].getAttribute("data-q")]===undefined){ setActive(i); return } }
    setActive(0);
  });

  el("printBtn").addEventListener("click",function(){
    var n=visibleCards().length;
    if(!n){ alert("В текущем фильтре нет вопросов."); return }
    var what = filter==="weak" ? "нули и единицы"
             : filter==="due"  ? "очередь повторения"
             : filter==="todo" ? "неоценённые"
             : query ? "результаты поиска" : "все вопросы";
    if(gfilter!=="all") what+=" (грейд "+gfilter+")";
    if(!confirm("Печатать "+what+" — "+n+" шт.? Ответы и заметки будут раскрыты.")) return;
    window.print();
  });

  el("collapse").addEventListener("click",function(){
    document.querySelectorAll("[data-ans]").forEach(function(a){a.hidden=true});
    cards.forEach(paint);
    window.scrollTo({top:0,behavior:"smooth"});
  });

  el("reset").addEventListener("click",function(){
    if(!confirm("Сбросить оценки, заметки и активность? Свои вопросы и дневник останутся.")) return;
    data.v={}; data.d={}; data.notes={}; data.days={};
    save(); collect(); recount(); applyFilter();
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
    if(e.target.closest("textarea,audio,input")) return;
    var dx=e.changedTouches[0].clientX-tx;
    if(Math.abs(dx)>70) setActive(activeIdx+(dx<0?1:-1));
  },{passive:true});

  // ── экзамен ──
  el("examBtn").addEventListener("click",function(){
    if(exam){ finishExam(true); return }
    el("examPanel").hidden=!el("examPanel").hidden;
    el("syncPanel").hidden=true; el("addPanel").hidden=true; el("statsPanel").hidden=true;
  });
  document.querySelectorAll("[data-exam]").forEach(function(btn){
    btn.addEventListener("click",function(){
      var n=parseInt(btn.getAttribute("data-exam"),10);
      el("examPanel").hidden=true;
      if(n>0) startExam(n);
    });
  });

  var examGrade="";
  function startExam(n){
    // если выбран грейд — экзамен идёт только по нему
    examGrade = gfilter==="all" ? "" : gfilter;
    var pool=cards.filter(function(c){
      return gfilter==="all" || c.getAttribute("data-grade")===gfilter;
    });
    if(pool.length<n){ pool=cards.slice(); examGrade="" }
    for(var i=pool.length-1;i>0;i--){ var j=Math.floor(Math.random()*(i+1)); var t=pool[i]; pool[i]=pool[j]; pool[j]=t }
    var chosen=pool.slice(0,Math.min(n,pool.length));
    exam={set:new Set(chosen.map(function(c){return c.getAttribute("data-q")})),total:chosen.length,
          ends:Date.now()+n*60000,tick:null};
    chosen.forEach(function(c){ var q=c.getAttribute("data-q"); delete data.v[q] });
    save();
    document.querySelectorAll("[data-ans]").forEach(function(a){a.hidden=true});
    el("examBtn").textContent="завершить"; el("examBtn").classList.add("on");
    el("resultPanel").hidden=true; query=""; el("search").value="";
    collect(); recount(); applyFilter(); setActive(0);
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
    var done=0; exam.set.forEach(function(q){ if(data.v[q]!==undefined) done++ });
    if(done>=exam.total) finishExam(false);
  }
  function finishExam(cancelled){
    if(!exam) return;
    clearInterval(exam.tick);
    var ids=Array.from(exam.set), c={0:0,1:0,2:0}, unrated=0;
    ids.forEach(function(q){ var v=data.v[q]; if(v===undefined) unrated++; else c[v]++ });
    var pct=Math.round(c["2"]/ids.length*100);
    exam=null;
    el("timer").hidden=true;
    el("examBtn").textContent="экзамен"; el("examBtn").classList.remove("on");
    if(!cancelled){
      var p=el("resultPanel");
      p.innerHTML='<p class="pt">Результат экзамена</p>'
        +'<p><span class="big2">'+pct+'%</span> уверенных ответов из '+ids.length+' вопросов</p>'
        +'<p class="pd">'+examBand(pct)+(examGrade?' Грейд: '+examGrade+'.':'')
        +' Уверенно: '+c["2"]+' · плыл: '+c["1"]+' · не знаю: '+c["0"]
        +(unrated?' · не дошёл: '+unrated:'')+'.</p>'
        +'<p class="pd">Всё, что ниже двойки, попало в очередь повторения.</p>'
        +'<div class="prow"><button class="chip" id="resClose" type="button">закрыть</button>'
        +'<button class="chip" id="resWeak" type="button">показать провалы</button></div>';
      p.hidden=false;
      el("resClose").addEventListener("click",function(){p.hidden=true});
      el("resWeak").addEventListener("click",function(){
        p.hidden=true; var w=document.querySelector('[data-filter="weak"]'); if(w) w.click();
      });
      window.scrollTo({top:0,behavior:"smooth"});
    }
    collect(); recount(); applyFilter();
  }

  // ── свой вопрос ──
  el("addBtn").addEventListener("click",function(){
    var p=el("addPanel"); p.hidden=!p.hidden;
    el("syncPanel").hidden=true; el("examPanel").hidden=true; el("statsPanel").hidden=true;
    if(!p.hidden) el("addQ").focus();
  });
  el("addClose").addEventListener("click",function(){ el("addPanel").hidden=true });
  el("addSave").addEventListener("click",function(){
    var q=el("addQ").value.trim(), a=el("addA").value.trim();
    if(!q){ el("addMsg").textContent="нужен хотя бы вопрос"; return }
    var maxId=0;
    data.custom.forEach(function(x){ var m=/^c(\d+)$/.exec(x.id); if(m) maxId=Math.max(maxId,+m[1]) });
    data.custom.push({id:"c"+(maxId+1),q:q,a:a||"— (ответ пока не записан)"});
    save(); renderCustom(); recount(); applyFilter();
    el("addQ").value=""; el("addA").value="";
    el("addMsg").textContent="добавлено, всего своих: "+data.custom.length;
  });

  // ── активность по дням ──
  el("statsBtn").addEventListener("click",function(){
    var p=el("statsPanel"); p.hidden=!p.hidden;
    el("syncPanel").hidden=true; el("examPanel").hidden=true; el("addPanel").hidden=true;
    if(!p.hidden) drawChart();
  });
  el("statsClose").addEventListener("click",function(){ el("statsPanel").hidden=true });

  function drawChart(){
    var t=today(), max=1, bars=[];
    for(var i=29;i>=0;i--){ var day=t-i, n=data.days[String(day)]||0; max=Math.max(max,n); bars.push([day,n]) }
    el("chart").innerHTML=bars.map(function(b){
      var h=Math.round(b[1]/max*100);
      var dt=new Date(b[0]*864e5);
      var label=dt.getDate()+"."+(dt.getMonth()+1)+" — "+(b[1]||0);
      return '<i class="'+(b[1]?"":"zero")+'" style="height:'+(b[1]?Math.max(h,6):4)+'%" data-t="'+label+'"></i>';
    }).join("");
    var streak=0;
    for(var k=0;k<400;k++){ if(data.days[String(t-k)]) streak++; else if(k>0) break; else break }
    var totalDays=Object.keys(data.days).length;
    var sum=0; for(var d2 in data.days) sum+=data.days[d2];
    el("streak").textContent="Серия: "+streak+" дн. подряд · дней с занятиями: "+totalDays
      +" · всего оценок поставлено: "+sum+". Тридцать дней по 25 минут обгоняют четыре героических выходных.";
  }

  // ── перенос ──
  el("syncBtn").addEventListener("click",function(){
    var p=el("syncPanel"); p.hidden=!p.hidden;
    el("examPanel").hidden=true; el("addPanel").hidden=true; el("statsPanel").hidden=true;
    if(!p.hidden){ el("syncBox").value=encodeState(); el("syncMsg").textContent="" }
  });
  el("syncClose").addEventListener("click",function(){ el("syncPanel").hidden=true });
  function encodeState(){
    try{ return "QA3:"+btoa(unescape(encodeURIComponent(JSON.stringify(data)))) }catch(e){ return "" }
  }
  function decodeState(str){
    str=(str||"").trim();
    var m=/^QA[23]:/.exec(str); if(m) str=str.slice(m[0].length);
    var o=JSON.parse(decodeURIComponent(escape(atob(str))));
    if(!o||typeof o!=="object"||!o.v) throw new Error("формат");
    return o;
  }
  el("syncCopy").addEventListener("click",function(){
    var box=el("syncBox"); box.value=encodeState(); box.select();
    var done=function(){ el("syncMsg").textContent="скопировано" };
    if(navigator.clipboard) navigator.clipboard.writeText(box.value).then(done,function(){document.execCommand("copy");done()});
    else { document.execCommand("copy"); done() }
  });
  el("syncApply").addEventListener("click",function(){
    try{
      var o=decodeState(el("syncBox").value);
      data={v:o.v||{},d:o.d||{},notes:o.notes||{},custom:o.custom||[],days:o.days||{},diary:o.diary||[]};
      save(); renderCustom(); recount(); applyFilter();
      el("syncMsg").textContent="применено: "+Object.keys(data.v).length+" оценок, "
        +Object.keys(data.notes).length+" заметок, "+data.custom.length+" своих вопросов";
    }catch(err){ el("syncMsg").textContent="не разобрал код" }
  });

  // ── переход по номеру: g, цифры, Enter ──
  var jumpBuf=null, jumpTimer=null;
  function showJump(){
    var j=el("jump"); j.hidden=false;
    j.textContent="перейти к вопросу: "+(jumpBuf||"…");
    clearTimeout(jumpTimer);
    jumpTimer=setTimeout(function(){ if(jumpBuf) doJump(); else cancelJump() },1600);
  }
  function cancelJump(){ jumpBuf=null; clearTimeout(jumpTimer); el("jump").hidden=true }
  function doJump(){
    var want=jumpBuf; cancelJump();
    if(!want) return;
    var card=document.getElementById("q"+parseInt(want,10));
    if(!card){
      var j=el("jump"); j.hidden=false; j.textContent="вопроса "+want+" нет";
      setTimeout(function(){ j.hidden=true },1400);
      return;
    }
    if(card.classList.contains("hide")){
      var all=document.querySelector('[data-filter="all"]');
      if(all) all.click();
      el("search").value=""; query=""; applyFilter();
    }
    setActive(visibleCards().indexOf(card));
  }

  // ── клавиатура ──
  document.addEventListener("keydown",function(e){
    var sb=el("search");
    var tag=(document.activeElement&&document.activeElement.tagName)||"";
    if(e.key==="/"&&document.activeElement!==sb&&tag!=="TEXTAREA"&&tag!=="INPUT"){ e.preventDefault(); sb.focus(); return }
    if(tag==="TEXTAREA"||tag==="INPUT"){ if(e.key==="Escape") document.activeElement.blur(); return }
    if(e.metaKey||e.ctrlKey||e.altKey) return;

    var k=e.key.toLowerCase();

    // g + номер + Enter (или пауза) — прыжок к вопросу
    if(jumpBuf!==null){
      if(/^[0-9]$/.test(e.key)){ e.preventDefault(); jumpBuf+=e.key; showJump(); return }
      if(e.key==="Enter"||e.key===" "){ e.preventDefault(); doJump(); return }
      if(e.key==="Escape"||e.key==="Backspace"){ e.preventDefault(); cancelJump(); return }
      cancelJump();
    }
    if(k==="g"){ e.preventDefault(); jumpBuf=""; showJump(); return }

    if(k==="j"||e.key==="ArrowRight"){ e.preventDefault(); setActive(activeIdx<0?0:activeIdx+1); return }
    if(k==="k"||e.key==="ArrowLeft"){ e.preventDefault(); setActive(activeIdx<0?0:activeIdx-1); return }

    var card=activeCard(); if(!card) return;
    if(e.key===" "||e.key==="Enter"){
      var btn=card.querySelector(".reveal");
      if(btn&&!btn.disabled){ e.preventDefault(); btn.click() }
      return;
    }
    if(k==="0"||k==="1"||k==="2"){
      e.preventDefault();
      var idx=visibleCards().indexOf(card);
      setVal(card,k);
      if(!exam&&!cardsMode&&(filter==="todo"||filter==="weak"||filter==="due")){
        applyFilter(); setActive(Math.min(idx,visibleCards().length-1));
      } else { applyFilter(); setActive(idx+1) }
      if(exam) maybeFinish();
      return;
    }
    if(k==="x"){ e.preventDefault(); setVal(card,null); applyFilter(); return }
    if(k==="n"){
      e.preventDefault();
      var nb=card.querySelector("[data-note]"); if(nb) nb.click();
      return;
    }
    if(k==="r"){
      e.preventDefault();
      var rb=card.querySelector("[data-rec]"); if(rb) rb.click();
    }
  });

  renderCustom(); collect(); recount(); applyFilter();
})();
</script>"""


EXTRAS = """<div class="extras">
  <button class="xbtn" type="button" data-note="%(n)d">заметка</button>
  <button class="xbtn" type="button" data-rec="%(n)d">записать ответ</button>
  <span class="recinfo mono" data-recinfo="%(n)d"></span>
</div>
<div class="notewrap" data-notewrap="%(n)d" hidden>
  <textarea data-noteta="%(n)d" rows="3" placeholder="Своими словами: как отвечал, где поплыл, что спросили на собеседовании"></textarea>
</div>
<div class="recwrap" data-recwrap="%(n)d" hidden></div>"""


SITE_NAV = """<nav class="sitenav"><div class="sitenav-in">
<a class="sbrand" href="./">nurekella<b>/</b>devops</a>
<a href="./">главная</a><a href="resume.html">резюме</a>
<a href="qa-trainer.html" aria-current="page">тренажёр</a>
<a href="roadmap.html">roadmap</a><a href="resources.html">материалы</a><a href="repos.html">репозитории</a><a href="checklist.html">чеклист</a><a href="devops-plan.html">план</a><a href="diary.html">дневник</a><a href="cv-review.html">разбор резюме</a>
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
.tsep{width:1px;height:18px;background:var(--line);display:inline-block}
.grades{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;margin:0 0 12px}
.gcard{background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:13px 15px;
  box-shadow:var(--shadow);cursor:pointer;transition:border-color .2s ease}
.gcard:hover{border-color:var(--accent)}
.gcard.picked{outline:2px solid var(--accent);outline-offset:-2px}
.gcard .gt{display:flex;justify-content:space-between;align-items:baseline;gap:8px;margin:0 0 9px;
  font-family:var(--mono);font-size:11px;letter-spacing:.09em;text-transform:uppercase;color:var(--ink-2)}
.gcard .gt .mono{color:var(--muted);letter-spacing:0}
.gbar{display:block;height:6px;background:var(--line-soft);border-radius:3px;overflow:hidden}
.gfill{display:block;height:100%;width:0;background:var(--accent);transition:width .3s ease}
.gcard .gs{margin:9px 0 0;font-size:.8rem;color:var(--muted);line-height:1.35}
.gcard.done{border-color:var(--s2)}
.gcard.done .gfill{background:var(--s2)}
.gcard.done .gt{color:var(--s2)}
.gcard.now{border-color:var(--accent)}
.gverdict{margin:0 0 22px;font-size:.9rem;color:var(--ink-2);max-width:var(--measure)}
@media (max-width:720px){.grades{grid-template-columns:1fr}}
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
.qh{display:grid;grid-template-columns:34px minmax(0,1fr) auto auto;gap:12px;align-items:baseline;
  margin-bottom:12px}
.qn{font-size:13px;color:var(--muted)}
.grade{font-size:10px;letter-spacing:.09em;text-transform:uppercase;padding:2px 7px;
  border-radius:999px;white-space:nowrap;border:1px solid var(--line);color:var(--muted)}
.grade[data-gr="junior"]{color:var(--s2);border-color:var(--s2);background:var(--s2b)}
.grade[data-gr="middle"]{color:var(--s1);border-color:var(--s1);background:var(--s1b)}
.grade[data-gr="senior"]{color:var(--s0);border-color:var(--s0);background:var(--s0b)}
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
.extras{display:flex;gap:7px;align-items:center;margin-top:10px;flex-wrap:wrap}
.xbtn{font-family:var(--mono);font-size:10.5px;letter-spacing:.05em;background:none;
  border:1px solid var(--line);color:var(--muted);padding:4px 9px;border-radius:6px;cursor:pointer}
.xbtn:hover{border-color:var(--accent);color:var(--accent)}
.xbtn.on{border-color:var(--accent);color:var(--accent);background:var(--accent-soft)}
.xbtn.rec{border-color:var(--s0);color:var(--s0);background:var(--s0b)}
.recinfo{font-size:10.5px;color:var(--muted)}
.q.hasnote .xbtn[data-note]{border-color:var(--s2);color:var(--s2)}
.notewrap{margin-top:9px}
.notewrap[hidden],.recwrap[hidden]{display:none}
.notewrap textarea{width:100%;font:inherit;font-size:.94rem;background:var(--surface-2);
  color:var(--ink);border:1px solid var(--line);border-radius:7px;padding:9px 11px;resize:vertical}
.recwrap{margin-top:9px}
.recwrap audio{width:100%;height:36px}
.panel input[type=text]{width:100%;font:inherit;font-size:.96rem;background:var(--surface-2);
  color:var(--ink);border:1px solid var(--line);border-radius:7px;padding:9px 11px;margin:0 0 9px}
#chart{display:flex;align-items:flex-end;gap:3px;height:64px;margin:0 0 12px;overflow-x:auto;padding-bottom:2px}
#chart i{flex:0 0 9px;background:var(--accent);border-radius:2px 2px 0 0;min-height:2px;position:relative}
#chart i.zero{background:var(--line)}
#chart i:hover::after{content:attr(data-t);position:absolute;bottom:100%;left:50%;
  transform:translateX(-50%);white-space:nowrap;font-family:var(--mono);font-size:10px;
  background:var(--ink);color:var(--bg);padding:2px 6px;border-radius:4px;margin-bottom:4px;z-index:5}
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
.jump{font-size:13px;background:var(--surface-2);border:1px solid var(--accent);color:var(--accent);
  border-radius:6px;padding:4px 9px;white-space:nowrap}
.jump[hidden]{display:none}
#dueN:empty{display:none}
.reveal.open{border-style:solid;border-color:var(--line);color:var(--muted);background:none}
.reveal.open:hover{border-color:var(--accent);color:var(--accent);background:var(--surface-2)}
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
@media print{
  /* Печатается ровно то, что сейчас в фильтре, с раскрытыми ответами и заметками. */
  .topbar,.sitenav,.rail,.keyhint,.panel,.cardnav,.progress,.rate,.extras,.reveal,
  .empty,.masthead,.prose.lead,.sub,.sect-score{display:none!important}
  body{background:#fff;color:#000;font-size:10.5pt}
  .shell{display:block;max-width:none;padding:0}
  .main{padding:0}
  .q.hide{display:none!important}
  .q{border:0;border-top:1px solid #bbb;border-radius:0;box-shadow:none;padding:10px 0;
     break-inside:avoid;page-break-inside:avoid}
  .q[data-v="0"],.q[data-v="1"],.q[data-v="2"]{border-left:0}
  .ans[hidden]{display:block!important}
  .notewrap[hidden]{display:block!important}
  .notewrap textarea{border:1px solid #bbb;background:#fff}
  .callout{background:#f4f4f4!important;border-left:2px solid #999}
  pre{background:#f4f4f4;border:1px solid #ddd}
  a{color:#000;text-decoration:none}
  a[href^="http"]::after{content:" (" attr(href) ")";font-size:8pt;color:#666}
  section{margin:0 0 8px}
  .sect-head{border:0;padding:0;margin:0 0 6px}
  h2{font-size:13pt;margin:14px 0 0}
  .qh{margin-bottom:6px}
  .mark{display:none}
  .grades,.gverdict{display:none}
  .grade{border:1px solid #999;color:#333;background:transparent!important}
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
      <span class="jump mono" id="jump" hidden></span>
    </div>
    <div class="tools">
      <input type="search" id="search" placeholder="поиск" aria-label="Поиск по вопросам">
      <button class="chip on" data-filter="all" type="button">все</button>
      <button class="chip" data-filter="todo" type="button">не оценено</button>
      <button class="chip" data-filter="weak" type="button">0 и 1</button>
      <button class="chip" data-filter="due" type="button">повторить <span id="dueN"></span></button>
      <span class="tsep" aria-hidden="true"></span>
      <button class="chip gchip on" data-grade-filter="all" type="button">все грейды</button>
      <button class="chip gchip" data-grade-filter="junior" type="button">junior</button>
      <button class="chip gchip" data-grade-filter="middle" type="button">middle</button>
      <button class="chip gchip" data-grade-filter="senior" type="button">senior</button>
      <span class="tsep" aria-hidden="true"></span>
      <button class="chip" id="resume" type="button">продолжить</button>
      <button class="chip" id="examBtn" type="button">экзамен</button>
      <button class="chip" id="cardsBtn" type="button">карточки</button>
      <button class="chip" id="addBtn" type="button">+ свой вопрос</button>
      <button class="chip" id="statsBtn" type="button">активность</button>
      <button class="chip" id="syncBtn" type="button">синхрон</button>
      <button class="chip" id="printBtn" type="button">печать</button>
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

    <div class="grades" id="gradeBox">
      <div class="gcard" data-gcard="junior">
        <p class="gt"><span>junior</span><span class="mono" data-glabel="junior">0 / 0</span></p>
        <span class="gbar"><span class="gfill" data-gfill="junior"></span></span>
        <p class="gs" data-gstate="junior">фундамент: отвечать без запинки</p>
      </div>
      <div class="gcard" data-gcard="middle">
        <p class="gt"><span>middle</span><span class="mono" data-glabel="middle">0 / 0</span></p>
        <span class="gbar"><span class="gfill" data-gfill="middle"></span></span>
        <p class="gs" data-gstate="middle">рабочий уровень: сюда целиться</p>
      </div>
      <div class="gcard" data-gcard="senior">
        <p class="gt"><span>senior</span><span class="mono" data-glabel="senior">0 / 0</span></p>
        <span class="gbar"><span class="gfill" data-gfill="senior"></span></span>
        <p class="gs" data-gstate="senior">масштаб, деньги, люди, риски</p>
      </div>
    </div>
    <p class="gverdict" id="gverdict">Грейд закрыт, когда двоек в нём 70% и больше. Начни с junior — на нём режут чаще, чем на Kubernetes.</p>

    <div class="panel" id="examPanel" hidden>
      <p class="pt">Режим экзамена</p>
      <p class="pd">Случайные вопросы, таймер, ответ открывается только после того, как ты поставил себе оценку. Так же, как на собеседовании: сначала отвечаешь, потом узнаёшь. Если выбран грейд, вопросы берутся только из него.</p>
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

    <div class="panel" id="addPanel" hidden>
      <p class="pt">Свой вопрос</p>
      <p class="pd">Спросили на собеседовании что-то, чего здесь нет — добавь. Попадёт в раздел «Мои вопросы», в оценки, в повторение и в код переноса.</p>
      <input type="text" id="addQ" placeholder="Вопрос" aria-label="Вопрос">
      <textarea id="addA" rows="4" placeholder="Ответ, как ты его понял" aria-label="Ответ"></textarea>
      <div class="prow">
        <button class="chip" id="addSave" type="button">добавить</button>
        <button class="chip" id="addClose" type="button">закрыть</button>
        <span class="pmsg" id="addMsg"></span>
      </div>
    </div>

    <div class="panel" id="statsPanel" hidden>
      <p class="pt">Активность по дням</p>
      <div id="chart"></div>
      <p class="pd" id="streak"></p>
      <div class="prow"><button class="chip" id="statsClose" type="button">закрыть</button></div>
    </div>

    <p class="keyhint">С клавиатуры: <kbd>Space</kbd> показать и скрыть ответ · <kbd>0</kbd> <kbd>1</kbd> <kbd>2</kbd> оценка ·
      <kbd>J</kbd> / <kbd>K</kbd> следующий и предыдущий вопрос · <kbd>N</kbd> заметка ·
      <kbd>R</kbd> запись · <kbd>G</kbd> + номер переход · <kbd>/</kbd> поиск</p>
    <p class="empty" id="empty" hidden>Ничего не найдено — измени запрос или фильтр.</p>
    {{BODY}}
    <section id="mine" data-sec="mine" hidden>
      <div class="sect-head"><h2>Мои вопросы</h2>
        <div class="sect-score"><span class="mono" id="mineCount">0</span></div>
      </div>
      <div id="mineList"></div>
    </section>
    <div class="cardnav" id="cardnav">
      <button type="button" id="cardPrev">← назад</button>
      <span class="pos" id="cardPos">—</span>
      <button type="button" id="cardNext">вперёд →</button>
    </div>
  </main>
</div>

{{SCRIPT}}
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
<script src="theme.js"></script>
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
