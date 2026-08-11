#!/usr/bin/env python3
"""Собирает страницу курсов (docs/course.html) из COURSE.md.

Формат урока в markdown:

    ### 1. Название урока

    `Грейд` junior
    `Время` 40 минут
    `Вопросы` 166, 167, 3

    `Зачем` Одна фраза о том, что даёт урок.

    **Теория.** …

    `Практика`

    ```bash
    команды
    ```

    `Проверка` Как понять, что получилось.

    `Типичная ошибка` …

`Грейд`, `Время` и `Вопросы` вырезаются из текста и становятся метаданными карточки:
грейд — значок и фильтр, время — оценка, вопросы — ссылки в тренажёр.
"""

import html
import re
import sys

from build_qa import blocks, inline, render, GRADES

SRC = "COURSE.md"
OUT = "docs/course.html"

META = ("Грейд", "Время", "Вопросы", "Зачем")
# blocks() склеивает соседние строки в один абзац, поэтому метаданные приходят одной строкой:
# «`Грейд` junior `Время` 30 минут `Вопросы` 195, 196» — режем её по маркерам.
META_RE = re.compile(r"`(%s)`\s*(.*?)(?=\s*`(?:%s)`|$)" % ("|".join(META), "|".join(META)))

NAV = """<nav class="topnav"><div class="topnav-in">
<a class="brand" href="index.html">nurekella<b>/</b>devops</a>
<a class="nl" href="index.html">главная</a>
<a class="nl" href="qa-trainer.html">тренажёр</a>
<a class="nl" href="course.html" aria-current="page">курсы</a>
<a class="nl" href="roadmap.html">roadmap</a>
<a class="nl" href="resources.html">материалы</a>
<a class="nl" href="repos.html">репозитории</a>
<a class="nl" href="checklist.html">чеклист</a>
<a class="nl" href="devops-plan.html">план</a>
<a class="nl" href="diary.html">дневник</a>
</div></nav>"""

STYLE = """<style>
  .bar{position:sticky;top:0;z-index:20;background:var(--bg);border-bottom:1px solid var(--line)}
  .bar-in{max-width:1240px;margin:0 auto;padding:11px 28px;display:flex;flex-wrap:wrap;
    align-items:center;gap:8px}
  .chip{font-family:var(--mono);font-size:11px;letter-spacing:.04em;background:var(--surface);
    border:1px solid var(--line);color:var(--muted);padding:6px 11px;border-radius:7px;cursor:pointer}
  .chip:hover{border-color:var(--accent);color:var(--accent)}
  .chip.on{background:var(--accent);border-color:var(--accent);color:var(--surface)}
  .barscore{display:flex;align-items:center;gap:10px;margin-right:auto;font-family:var(--mono);
    font-size:11px;color:var(--muted);letter-spacing:.04em}
  .barscore .big{font-size:1.2rem;color:var(--accent);letter-spacing:-.02em}
  .barscore .meter{width:96px;height:5px;background:var(--line-soft);border-radius:3px;overflow:hidden;display:block}
  .barscore .mfill{display:block;height:100%;width:0;background:var(--accent);transition:width .3s ease}
  .tsep{width:1px;height:18px;background:var(--line);display:inline-block}

  .grades{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;margin:0 0 12px}
  .gcard{background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:13px 15px;
    box-shadow:var(--shadow);cursor:pointer;transition:border-color .2s ease}
  .gcard:hover{border-color:var(--accent)}
  .gcard.picked{outline:2px solid var(--accent);outline-offset:-2px}
  .gcard .gt{display:flex;justify-content:space-between;align-items:baseline;gap:8px;margin:0 0 9px;
    font-family:var(--mono);font-size:11px;letter-spacing:.09em;text-transform:uppercase;color:var(--ink-2)}
  .gcard .gt span:last-child{color:var(--muted);letter-spacing:0}
  .gbar{display:block;height:6px;background:var(--line-soft);border-radius:3px;overflow:hidden}
  .gfill{display:block;height:100%;width:0;background:var(--accent);transition:width .3s ease}
  .gcard .gs{margin:9px 0 0;font-size:.8rem;color:var(--muted);line-height:1.35}
  .gcard.done{border-color:var(--s2)}
  .gcard.done .gfill{background:var(--s2)}
  .gcard.done .gt{color:var(--s2)}
  .gverdict{margin:0 0 26px;font-size:.9rem;color:var(--ink-2);max-width:var(--measure)}
  @media (max-width:720px){.grades{grid-template-columns:1fr}}

  .track h2{font-family:var(--mono);font-size:12px;letter-spacing:.14em;text-transform:uppercase;
    color:var(--ink-2);margin:34px 0 4px}
  .track .lead{font-size:.92rem;color:var(--muted);margin:0 0 16px;max-width:var(--measure)}

  .lesson{background:var(--surface);border:1px solid var(--line);border-radius:11px;
    margin:0 0 10px;box-shadow:var(--shadow);overflow:hidden}
  .lesson[hidden]{display:none}
  .lesson.done{border-color:var(--s2)}
  .lhead{display:flex;align-items:flex-start;gap:12px;padding:15px 18px;cursor:pointer}
  .lhead:hover{background:var(--surface-2)}
  .tick{appearance:none;-webkit-appearance:none;width:18px;height:18px;flex:none;margin-top:2px;
    border:1.5px solid var(--line);border-radius:5px;background:var(--surface);position:relative;cursor:pointer}
  .tick:hover{border-color:var(--accent)}
  .tick:checked{background:var(--s2,#1C6B4B);border-color:var(--s2,#1C6B4B)}
  .tick:checked::after{content:"";position:absolute;left:5.5px;top:2px;width:4px;height:9px;
    border:solid var(--surface);border-width:0 1.8px 1.8px 0;transform:rotate(45deg)}
  .lt{flex:1;min-width:0}
  .lt h3{margin:0;font-size:1.06rem;line-height:1.3}
  .lesson.done .lt h3{color:var(--muted)}
  .lwhy{margin:5px 0 0;font-size:.9rem;color:var(--ink-2);line-height:1.4}
  .lmeta{display:flex;flex-wrap:wrap;gap:6px;align-items:center;margin:8px 0 0}
  .grade{font-family:var(--mono);font-size:9.5px;letter-spacing:.09em;text-transform:uppercase;
    padding:2px 7px;border-radius:999px;border:1px solid var(--line);color:var(--muted)}
  .grade[data-gr="junior"]{color:var(--s2);border-color:var(--s2);background:var(--s2b)}
  .grade[data-gr="middle"]{color:var(--s1);border-color:var(--s1);background:var(--s1b)}
  .grade[data-gr="senior"]{color:var(--s0);border-color:var(--s0);background:var(--s0b)}
  .time{font-family:var(--mono);font-size:9.5px;letter-spacing:.07em;text-transform:uppercase;
    color:var(--muted);border:1px solid var(--line-soft);border-radius:999px;padding:2px 7px}
  .num{font-family:var(--mono);font-size:12px;color:var(--muted);min-width:24px}
  .toggle{font-family:var(--mono);font-size:10px;letter-spacing:.08em;text-transform:uppercase;
    color:var(--muted);border:1px solid var(--line);border-radius:6px;padding:4px 9px;background:var(--surface);
    cursor:pointer;white-space:nowrap;flex:none}
  .lesson.open .toggle{border-color:var(--accent);color:var(--accent)}
  .lbody{padding:0 18px 18px;border-top:1px solid var(--line-soft);margin-top:0}
  .lbody[hidden]{display:none}
  .lbody h4{margin:20px 0 8px;font-size:.98rem}
  .lbody pre{margin:0 0 14px;background:var(--surface-2);border:1px solid var(--line-soft);
    border-radius:8px;padding:14px 16px;overflow-x:auto}
  .lbody pre code{background:none;border:0;padding:0;font-size:.83rem;line-height:1.55}
  .lbody .callout{border-left:2px solid var(--line);background:var(--surface-2);
    padding:10px 15px;border-radius:0 6px 6px 0;margin:0 0 12px;max-width:var(--measure);font-size:.94rem}
  .lbody .callout .clabel{display:block;font-family:var(--mono);font-size:10px;letter-spacing:.12em;
    text-transform:uppercase;margin-bottom:5px;color:var(--muted)}
  .lbody .step{font-family:var(--mono);font-size:10.5px;letter-spacing:.13em;text-transform:uppercase;
    color:var(--accent);margin:20px 0 9px;padding-left:9px;border-left:2px solid var(--accent)}
  .lbody .callout.do{border-left-color:var(--accent);background:var(--accent-soft)}
  .lbody .callout.check{border-left-color:var(--s2,#1C6B4B)}
  .lbody .callout.trap{border-left-color:var(--s0,#A33A32)}
  .lbody .sub-list{margin:6px 0 0;padding-left:1.15em}
  .qlinks{display:flex;flex-wrap:wrap;gap:5px;align-items:center;margin:16px 0 0;
    padding-top:13px;border-top:1px solid var(--line-soft)}
  .qlinks .ql{font-family:var(--mono);font-size:10px;letter-spacing:.09em;text-transform:uppercase;
    color:var(--muted);margin-right:4px}
  .qlinks a{font-family:var(--mono);font-size:11px;text-decoration:none;border:1px solid var(--line);
    color:var(--muted);padding:3px 8px;border-radius:6px}
  .qlinks a:hover{border-color:var(--accent);color:var(--accent)}
  .empty{color:var(--muted);font-size:.94rem;margin:20px 0}
  .empty[hidden]{display:none}
  @media (max-width:900px){ .bar-in{padding:10px 18px} .lhead{padding:13px 15px} .lbody{padding:0 15px 15px} }
  @media print{
    .bar,.topnav,.grades,.gverdict{display:none}
    .lbody[hidden]{display:block!important}
    .lesson{break-inside:avoid;border:1px solid #999;box-shadow:none}
    .toggle,.tick{display:none}
    body{background:#fff;color:#000}
  }
</style>"""

SCRIPT = r"""<script>
(function(){
  var KEY="qa-course-v1";
  var el=function(id){return document.getElementById(id)};
  var GRADES=["junior","middle","senior"];
  var GNOTE={
    junior:"Собрать руками то, что спрашивают в первые пять минут собеседования.",
    middle:"Эксплуатация: то, за что платят на целевых вакансиях.",
    senior:"Масштаб, отказоустойчивость, деньги и процессы."
  };

  var state={};
  try{ state=JSON.parse(localStorage.getItem(KEY))||{} }catch(e){ state={} }
  function save(){ try{localStorage.setItem(KEY,JSON.stringify(state))}catch(e){} }

  var lessons=Array.prototype.slice.call(document.querySelectorAll(".lesson"));
  var gfilter="all", todoOnly=false;

  function isDone(n){ return !!state[n] }

  function paint(l){
    var n=l.getAttribute("data-n"), on=isDone(n);
    l.classList.toggle("done",on);
    var t=l.querySelector(".tick"); if(t) t.checked=on;
  }

  function openLesson(l,on){
    var b=l.querySelector(".lbody");
    if(!b) return;
    b.hidden=!on;
    l.classList.toggle("open",on);
    var t=l.querySelector(".toggle");
    if(t) t.textContent=on?"свернуть":"открыть урок";
  }

  function apply(){
    var shown=0;
    lessons.forEach(function(l){
      var ok=true;
      if(gfilter!=="all" && l.getAttribute("data-grade")!==gfilter) ok=false;
      if(ok&&todoOnly&&isDone(l.getAttribute("data-n"))) ok=false;
      l.hidden=!ok;
      if(ok) shown++;
    });
    document.querySelectorAll("[data-track]").forEach(function(tr){
      var any=Array.prototype.some.call(tr.querySelectorAll(".lesson"),function(l){return !l.hidden});
      tr.hidden=!any;
    });
    el("empty").hidden=shown>0;
  }

  function stats(){
    var g={};
    GRADES.forEach(function(k){ g[k]={done:0,tot:0,min:0,left:0} });
    lessons.forEach(function(l){
      var k=l.getAttribute("data-grade"); if(!g[k]) return;
      var m=+l.getAttribute("data-min")||0;
      g[k].tot++; g[k].min+=m;
      if(isDone(l.getAttribute("data-n"))) g[k].done++; else g[k].left+=m;
    });
    return g;
  }

  function hours(m){
    if(m<60) return m+" мин";
    var h=Math.floor(m/60), r=m%60;
    return h+" ч"+(r?" "+r+" мин":"");
  }

  function recount(){
    var g=stats(), done=0, tot=0, left=0, current=null;
    GRADES.forEach(function(k){
      var x=g[k], r=x.tot?x.done/x.tot:0, full=(x.tot>0&&x.done===x.tot);
      done+=x.done; tot+=x.tot; left+=x.left;
      var lb=document.querySelector('[data-glabel="'+k+'"]');
      if(lb) lb.textContent=x.done+" / "+x.tot+" · "+hours(x.min);
      var f=document.querySelector('[data-gfill="'+k+'"]'); if(f) f.style.width=(r*100)+"%";
      var card=document.querySelector('[data-gcard="'+k+'"]');
      if(card) card.classList.toggle("done",full);
      var st=document.querySelector('[data-gstate="'+k+'"]');
      if(st) st.textContent = full ? "пройден целиком"
        : (x.done===0 ? GNOTE[k] : "осталось "+(x.tot-x.done)+" уроков, "+hours(x.left));
      if(!full && current===null) current=k;
    });
    var pct=tot?Math.round(done/tot*100):0;
    el("pct").textContent=pct+"%";
    el("mfill").style.width=pct+"%";
    el("score").textContent=done+" из "+tot+" уроков · осталось "+hours(left);
    var v=el("gverdict");
    if(v){
      v.textContent = current===null
        ? "Курс пройден целиком. Дальше учит только прод и собеседования — иди откликайся."
        : done===0
          ? "Начни с первого урока junior. Один урок в день — это "+Math.ceil(tot/7)+" недель до конца курса, и почти всё время уходит на практику, а не на чтение."
          : "Сейчас идёшь по "+current+". Урок считается пройденным, когда сделана практика, а не когда прочитан текст.";
    }
  }

  // ── события ──
  document.addEventListener("click",function(e){
    if(e.target.closest(".tick")) return;          // галочку обрабатывает change
    if(e.target.closest(".lbody")) return;         // клики внутри урока не сворачивают его
    var h=e.target.closest(".lhead");
    if(h){
      var l=h.closest(".lesson");
      openLesson(l, l.querySelector(".lbody").hidden);
      return;
    }
    var g=e.target.closest("[data-gcard]");
    if(g){
      var k=g.getAttribute("data-gcard");
      var btn=document.querySelector('[data-gf="'+(gfilter===k?"all":k)+'"]');
      if(btn) btn.click();
    }
  });

  document.addEventListener("change",function(e){
    var t=e.target.closest(".tick");
    if(!t) return;
    var l=t.closest(".lesson"), n=l.getAttribute("data-n");
    if(t.checked) state[n]=1; else delete state[n];
    save(); paint(l); recount(); if(todoOnly) apply();
  });

  document.querySelectorAll("[data-gf]").forEach(function(b){
    b.addEventListener("click",function(){
      document.querySelectorAll("[data-gf]").forEach(function(x){x.classList.remove("on")});
      b.classList.add("on"); gfilter=b.getAttribute("data-gf"); apply();
      document.querySelectorAll("[data-gcard]").forEach(function(c){
        c.classList.toggle("picked",gfilter!=="all"&&c.getAttribute("data-gcard")===gfilter);
      });
    });
  });

  el("onlyTodo").addEventListener("click",function(){
    todoOnly=!todoOnly;
    el("onlyTodo").classList.toggle("on",todoOnly);
    apply();
  });

  el("expandAll").addEventListener("click",function(){
    var anyClosed=lessons.some(function(l){return !l.hidden && l.querySelector(".lbody").hidden});
    lessons.forEach(function(l){ if(!l.hidden) openLesson(l,anyClosed) });
    el("expandAll").textContent=anyClosed?"свернуть все":"раскрыть все";
  });

  el("next").addEventListener("click",function(){
    for(var i=0;i<lessons.length;i++){
      var l=lessons[i];
      if(!isDone(l.getAttribute("data-n"))){
        document.querySelector('[data-gf="all"]').click();
        openLesson(l,true);
        l.scrollIntoView({block:"start",behavior:"smooth"});
        return;
      }
    }
    alert("Все уроки отмечены как пройденные.");
  });

  el("reset").addEventListener("click",function(){
    if(!confirm("Снять отметки со всех уроков?")) return;
    state={}; save(); lessons.forEach(paint); recount(); apply();
  });

  lessons.forEach(paint);
  recount(); apply();
})();
</script>"""

TEMPLATE = """<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%(title)s</title>
<meta name="description" content="%(desc)s">
<meta name="theme-color" content="#EFF1F3" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#0F1319" media="(prefers-color-scheme: dark)">
<link rel="stylesheet" href="style.css">
<link rel="manifest" href="manifest.webmanifest">
<script src="theme.js"></script>
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>&#9096;</text></svg>">
%(style)s
</head>
<body>
%(nav)s

<div class="bar">
  <div class="bar-in">
    <span class="barscore">
      <span class="big" id="pct">0%%</span>
      <span class="meter"><span class="mfill" id="mfill"></span></span>
      <span id="score">0 из 0 уроков</span>
    </span>
    <button class="chip on" data-gf="all" type="button">все грейды</button>
    <button class="chip" data-gf="junior" type="button">junior</button>
    <button class="chip" data-gf="middle" type="button">middle</button>
    <button class="chip" data-gf="senior" type="button">senior</button>
    <span class="tsep" aria-hidden="true"></span>
    <button class="chip" id="next" type="button">следующий урок</button>
    <button class="chip" id="onlyTodo" type="button">только непройденные</button>
    <button class="chip" id="expandAll" type="button">раскрыть все</button>
    <button class="chip" id="reset" type="button">сбросить</button>
  </div>
</div>

<div class="wrap">
  <header class="masthead">
    <p class="eyebrow">Курсы</p>
    <h1>%(h1)s</h1>
    <div class="prose lead">%(intro)s</div>
  </header>

  <div class="grades">
    <div class="gcard" data-gcard="junior">
      <p class="gt"><span>junior</span><span data-glabel="junior">0 / 0</span></p>
      <span class="gbar"><span class="gfill" data-gfill="junior"></span></span>
      <p class="gs" data-gstate="junior"></p>
    </div>
    <div class="gcard" data-gcard="middle">
      <p class="gt"><span>middle</span><span data-glabel="middle">0 / 0</span></p>
      <span class="gbar"><span class="gfill" data-gfill="middle"></span></span>
      <p class="gs" data-gstate="middle"></p>
    </div>
    <div class="gcard" data-gcard="senior">
      <p class="gt"><span>senior</span><span data-glabel="senior">0 / 0</span></p>
      <span class="gbar"><span class="gfill" data-gfill="senior"></span></span>
      <p class="gs" data-gstate="senior"></p>
    </div>
  </div>
  <p class="gverdict" id="gverdict"></p>

%(body)s
  <p class="empty" id="empty" hidden>В этом фильтре уроков нет.</p>

  <footer class="site">
    <p>Уроки написаны под <a href="qa-trainer.html">тренажёр</a>: каждый закрывает конкретные вопросы, их номера стоят в конце урока. Порядок прохождения — как в <a href="roadmap.html">roadmap</a>. Ссылки на внешние курсы и репозитории — на страницах <a href="resources.html">материалов</a> и <a href="repos.html">репозиториев</a>.</p>
  </footer>
</div>
%(script)s
</body>
</html>
"""

CALLOUT_CLS = {
    "Практика": "do",
    "Проверка": "check",
    "Типичная ошибка": "trap",
    "Итог": "check",
}


def parse(text):
    """Разбирает COURSE.md на вводную часть и треки с уроками."""
    lines = text.split("\n")
    title, intro = "", []
    tracks, cur = [], None
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("# ") and not title:
            title = line[2:].strip()
            i += 1
            continue
        if line.startswith("## "):
            cur = {"title": line[3:].strip(), "lead": [], "lessons": []}
            tracks.append(cur)
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
            meta, rest = {}, []
            for kind, payload in bs:
                if kind == "p" and isinstance(payload, str) \
                        and payload.startswith(tuple("`%s`" % k for k in META)):
                    for key, val in META_RE.findall(payload):
                        meta[key] = val.strip()
                    continue
                rest.append((kind, payload))
            cur["lessons"].append({
                "num": int(m.group(1)) if m else None,
                "title": m.group(2) if m else heading,
                "meta": meta,
                "blocks": rest,
            })
            continue
        (cur["lead"] if cur else intro).append(line)
        i += 1
    return title, blocks(intro), tracks


def render_body(bs):
    """Как render(), но с дополнительными типами выносок урока."""
    out = []
    for kind, payload in bs:
        if kind == "p" and isinstance(payload, str):
            marker = None
            text = payload
            for k in CALLOUT_CLS:
                if text.startswith("`%s`" % k):
                    marker = k
                    text = text[len(k) + 2:].strip()
                    break
            if marker:
                if not text:
                    # маркер без текста — это заголовок шага перед кодом, а не выноска
                    out.append('<p class="step %s">%s</p>' % (CALLOUT_CLS[marker], marker))
                else:
                    out.append('<div class="callout %s"><span class="clabel">%s</span>%s</div>'
                               % (CALLOUT_CLS[marker], marker, inline(text)))
                continue
        out.append(render([(kind, payload)]))
    return "\n".join(out)


def minutes(t):
    m = re.search(r"(\d+)", t or "")
    return int(m.group(1)) if m else 0


def build(title, intro_blocks, tracks):
    body, total = [], 0
    for tr in tracks:
        body.append('<section class="track" data-track="%s">' % html.escape(tr["title"]))
        body.append("<h2>%s</h2>" % inline(tr["title"]))
        lead = render(blocks(tr["lead"]))
        if lead.strip():
            body.append('<div class="lead">%s</div>' % re.sub(r"</?p>", "", lead))
        for ls in tr["lessons"]:
            if not ls["num"]:
                continue
            total += 1
            grade = (ls["meta"].get("Грейд") or "junior").lower()
            if grade not in GRADES:
                grade = "junior"
            tm = ls["meta"].get("Время", "")
            why = ls["meta"].get("Зачем", "")
            qs = [q.strip() for q in re.split(r"[,\s]+", ls["meta"].get("Вопросы", "")) if q.strip().isdigit()]
            n = ls["num"]

            body.append('<article class="lesson" id="l%d" data-n="%d" data-grade="%s" data-min="%d">'
                        % (n, n, grade, minutes(tm)))
            body.append('<div class="lhead">')
            body.append('<input class="tick" type="checkbox" aria-label="Отметить урок %d пройденным">' % n)
            body.append('<div class="lt"><h3><span class="num">%02d</span> %s</h3>' % (n, inline(ls["title"])))
            if why:
                body.append('<p class="lwhy">%s</p>' % inline(why))
            body.append('<div class="lmeta"><span class="grade" data-gr="%s">%s</span>' % (grade, grade))
            if tm:
                body.append('<span class="time">%s</span>' % html.escape(tm))
            body.append("</div></div>")
            body.append('<button class="toggle" type="button">открыть урок</button>')
            body.append("</div>")
            body.append('<div class="lbody" hidden>')
            body.append(render_body(ls["blocks"]))
            if qs:
                body.append('<div class="qlinks"><span class="ql">Закрывает вопросы</span>'
                            + "".join('<a href="qa-trainer.html#q%s">%s</a>' % (q, q) for q in qs)
                            + "</div>")
            body.append("</div></article>")
        body.append("</section>")

    return TEMPLATE % {
        "title": "Курсы DevOps по грейдам — уроки с практикой",
        "desc": ("Курс DevOps своими уроками по грейдам junior, middle, senior: короткая теория, "
                 "практика с командами, проверка результата и вопросы тренажёра, которые урок закрывает."),
        "h1": html.escape(title or "Курсы"),
        "intro": render(intro_blocks),
        "nav": NAV,
        "style": STYLE,
        "script": SCRIPT,
        "body": "\n".join(body),
    }


def main():
    src, out = SRC, OUT
    args = sys.argv[1:]
    if "-o" in args:
        out = args[args.index("-o") + 1]
    with open(src, encoding="utf-8") as fh:
        title, intro, tracks = parse(fh.read())
    page = build(title, intro, tracks)
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(page)
    n = sum(1 for tr in tracks for ls in tr["lessons"] if ls["num"])
    mins = sum(minutes(ls["meta"].get("Время", "")) for tr in tracks for ls in tr["lessons"] if ls["num"])
    print("%s: треков=%d уроков=%d времени=%d мин (%.1f ч) chars=%d"
          % (out, len(tracks), n, mins, mins / 60.0, len(page)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
