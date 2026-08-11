/* Переключение темы вручную. Подключается в <head> всех страниц:
   сначала применяет сохранённый выбор (до отрисовки, чтобы не мигало),
   потом добавляет кнопку в меню. Три состояния: системная / светлая / тёмная. */
(function () {
  var KEY = "qa-theme";
  var ORDER = ["auto", "light", "dark"];
  var LABEL = { auto: "тема: как в системе", light: "тема: светлая", dark: "тема: тёмная" };
  var ICON = { auto: "◐", light: "☀", dark: "☾" };

  function read() {
    try { return localStorage.getItem(KEY) || "auto"; } catch (e) { return "auto"; }
  }

  function apply(mode) {
    var root = document.documentElement;
    if (mode === "auto") root.removeAttribute("data-theme");
    else root.setAttribute("data-theme", mode);
    // Полоска браузера должна совпадать с фактической темой.
    var dark = mode === "dark" ||
      (mode === "auto" && window.matchMedia &&
       window.matchMedia("(prefers-color-scheme: dark)").matches);
    document.querySelectorAll('meta[name="theme-color"]').forEach(function (m) {
      m.setAttribute("content", dark ? "#0F1319" : "#EFF1F3");
      m.removeAttribute("media");
    });
  }

  // до отрисовки
  apply(read());

  function mount() {
    var bar = document.querySelector(".topnav-in") || document.querySelector(".sitenav-in");
    if (!bar || document.getElementById("themeBtn")) return;

    var btn = document.createElement("button");
    btn.id = "themeBtn";
    btn.type = "button";
    btn.title = "Переключить тему";
    btn.setAttribute("aria-label", "Переключить тему");
    btn.style.cssText =
      "font-family:var(--mono);font-size:12px;background:none;border:1px solid var(--line);" +
      "color:var(--muted);padding:4px 9px;border-radius:6px;cursor:pointer;line-height:1.4";

    function paint() {
      var m = read();
      btn.textContent = ICON[m];
      btn.title = LABEL[m] + " — нажми, чтобы сменить";
    }

    btn.addEventListener("click", function () {
      var next = ORDER[(ORDER.indexOf(read()) + 1) % ORDER.length];
      try { localStorage.setItem(KEY, next); } catch (e) {}
      apply(next);
      paint();
    });

    paint();
    bar.appendChild(btn);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", mount);
  } else {
    mount();
  }

  // Если выбран «как в системе», следим за сменой системной темы.
  if (window.matchMedia) {
    window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", function () {
      if (read() === "auto") apply("auto");
    });
  }
})();
