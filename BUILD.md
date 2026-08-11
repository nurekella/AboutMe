# Как пересобрать сайт

Сайт лежит в `docs/` и отдаётся GitHub Pages. Источники правды — markdown-файлы
в корне репозитория; HTML в `docs/` собирается из них.

```bash
# тренажёр из INTERVIEW_QA.md
python3 tools/build_qa.py

# страница разбора резюме из CV_REVIEW.md
cd tools && python3 build_page.py ../CV_REVIEW.md ../docs/cv-review.html \
  "Разбор резюме — Нурбол Хамзаулы" cv-review.html && cd ..
```

`index.html`, `resume.html`, `devops-plan.html` и `style.css` написаны руками —
их правят напрямую.

Тренажёр умеет два режима вывода:

```bash
python3 tools/build_qa.py                       # полный документ → docs/qa-trainer.html
python3 tools/build_qa.py --fragment -o out.html  # фрагмент без <head>, для встраивания
```

Страница материалов собирается так же:

```bash
cd tools && python3 build_page.py ../RESOURCES.md ../docs/resources.html \
  "Материалы: курсы, книги, видео, лабы" resources.html && cd ..
```

`roadmap.html`, `checklist.html`, `diary.html` и `theme.js` написаны руками.
