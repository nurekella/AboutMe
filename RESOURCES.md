# Материалы: курсы, книги, видео, лабы

Отобранное, а не собранное. На каждую тему — один основной источник и один справочный; остальное в конце, в разделе «чего не надо».

Правило, которое важнее списка: **источников в работе не больше двух одновременно.** Переключение курсов — самая приятная форма прокрастинации: ощущается как работа, результата не даёт.

---

## Порядок

Если начинать сегодня, порядок такой:

1. **Руками в браузере** — [escbash](https://www.escbash.com/) или Killercoda, чтобы сразу трогать, а не смотреть.
2. **Рамка** — Kubernetes-курс Nana на YouTube, бесплатно, чтобы понять «зачем».
3. **Как это на работе** — Abhishek Veeramalla, разборы реальных задач и собеседований.
4. **Глубина** — документация Kubernetes и одна книга.
5. **Проверка** — [тренажёр](qa-trainer.html) и мок-экзамены CKA.

Дальше по разделам — что именно брать.

---

## Интерактивные лабы: учиться руками

Просмотренное видео не равно навыку. Это единственная категория, где навык появляется сразу, поэтому она первая.

### escbash

[escbash.com](https://www.escbash.com/) — браузерные лабы **на настоящих машинах**, а не в симуляторе: свежая Linux-машина под каждую задачу, реальные команды, проверка отправленного решения с оценкой. Для облачных лаб выдаётся живой AWS-аккаунт.

Есть готовые роадмапы (DevOps Engineer — 7+ навыков, около 113 часов) и отдельные навыки: Linux, Shell, Docker, Kubernetes, Python для DevOps, Go, AWS.

Чем ценно именно тебе: ты жалуешься, что бросаешь. Формат «задача → выполнил → получил оценку» держит внимание лучше, чем видеокурс, где прогресс измеряется просмотренными минутами.

### Killercoda

[killercoda.com](https://killercoda.com/) — бесплатные сценарии в браузере, включая полные наборы под **CKA, CKAD, CKS**. Лучшее место тренировать скорость с `kubectl`: на экзамене и на техническом собеседовании с живым кластером решает не знание, а скорость.

### KodeKloud

[kodekloud.com](https://kodekloud.com/) — курсы Mumshad Mannambeth с лабами. Его курс по CKA считается эталонным для подготовки к экзамену. Есть бесплатный уровень.

### iximiuz Labs

[labs.iximiuz.com](https://labs.iximiuz.com/) — Иван Величко, глубоко про внутренности контейнеров и Kubernetes. Сюда идти, когда захочется понять, что под капотом, а не как пользоваться.

### Своя песочница

Отдельно и бесплатно: **сломай свой кластер специально.** Убей etcd. Заполни диск на узле. Поставь `memory limit` в 10Mi. Сломай CoreDNS. Испорти RBAC так, чтобы под не смог читать Secret. Каждая поломка — это вопрос из тренажёра, прожитый руками, и он больше не забудется.

---

## Курсы

### TechWorld with Nana

[techworld-with-nana.com](https://www.techworld-with-nana.com/) — сильная сторона в том, что объясняется **зачем** технология существует и как встраивается в картину, а не только какие команды нажимать. Именно этого не хватает при переходе из администраторов: детали есть, нужна рамка.

| Что | Формат | Кому |
|---|---|---|
| **DevOps Bootcamp** | 6 месяцев, уровень с нуля, с проектами | Основной продукт. Брать, если нужен внешний дедлайн и структура |
| **DevSecOps Bootcamp** | 4 месяца, продвинутый | Логичное продолжение при банковском бэкграунде — security становится преимуществом |
| **GitLab CI/CD** | отдельный курс | Точечно, если GitLab CI твой основной инструмент |
| **IT Fundamentals** | мини-буткамп | Пропустить: это про жизненный цикл разработки для новичков |
| **Роадмапы** | бесплатно на сайте | Скачать, сверить со своим планом |

Честно про платное: буткамп на шесть месяцев имеет смысл, только если ты доводишь его до конца. При привычке бросать деньги и группа держат лучше, чем сила воли — но одно, а не коллекция курсов.

### Abhishek Veeramalla

Сильная сторона противоположная и дополняющая: **как это выглядит на реальной работе.** Разбор задач «день из жизни DevOps-инженера», реальные пайплайны, много про собеседования и про то, как формулировать ответы. Серии «Zero to Hero» по Kubernetes, Docker, Terraform, Ansible, AWS, GitOps.

Как совмещать: Nana — чтобы понять, Abhishek — чтобы понять, как это применяют и как об этом говорят.

### Русскоязычные интенсивы

Слёрм, Rebrain, Southbridge — формат «две недели, много практики, жёсткий дедлайн» работает против привычки бросать. Это добавка к плану, а не замена ему.

---

## Видео на YouTube

Каналы целиком плюс поиск по названию — так ссылки не гниют.

### Основное

| Канал | Что смотреть |
|---|---|
| [TechWorld with Nana](https://www.youtube.com/@TechWorldwithNana/videos) | [Kubernetes Tutorial for Beginners](https://www.youtube.com/results?search_query=techworld+with+nana+kubernetes+tutorial+for+beginners) (~4 ч) — главное видео канала, смотреть с кластером под рукой. Затем [Docker Tutorial](https://www.youtube.com/results?search_query=techworld+with+nana+docker+tutorial+for+beginners), [Terraform](https://www.youtube.com/results?search_query=techworld+with+nana+terraform+course), [Helm](https://www.youtube.com/results?search_query=techworld+with+nana+helm), [Prometheus](https://www.youtube.com/results?search_query=techworld+with+nana+prometheus+monitoring), [GitLab CI/CD](https://www.youtube.com/results?search_query=techworld+with+nana+gitlab+ci+cd) |
| [Abhishek Veeramalla](https://www.youtube.com/@AbhishekVeeramalla/videos) | Серии «Zero to Hero», разборы собеседований, «day-to-day activities of a DevOps engineer» |

### Дополнительно

| Канал | Чем полезен |
|---|---|
| [That DevOps Guy (Marcel Dempers)](https://www.youtube.com/@MarcelDempers/videos) | Практические разборы инструментов Kubernetes, коротко и по делу |
| [DevOps Toolkit (Viktor Farcic)](https://www.youtube.com/@DevOpsToolkit/videos) | Обзоры и сравнения — чтобы понимать ландшафт, а не один инструмент |
| [Anton Putra](https://www.youtube.com/@AntonPutra/videos) | Бенчмарки с цифрами: что быстрее и почему |
| [CNCF](https://www.youtube.com/@cncf/videos) | Доклады KubeCon — бесплатно, уровень выше любого курса |
| [Kubernetes Podcast](https://kubernetespodcast.com/) | В дорогу, чтобы держать контекст индустрии |

Полезные конкретные темы, которые стоит найти и посмотреть один раз:
[что происходит при kubectl apply](https://www.youtube.com/results?search_query=what+happens+when+you+run+kubectl+apply+explained),
[eBPF и Cilium — зачем заменяют kube-proxy](https://www.youtube.com/results?search_query=ebpf+cilium+replace+kube-proxy+explained),
[Gateway API вместо Ingress](https://www.youtube.com/results?search_query=kubernetes+gateway+api+vs+ingress),
[ArgoCD за 20 минут](https://www.youtube.com/results?search_query=argocd+tutorial+gitops+kubernetes).

---

## Книги

По одной, а не коллекцией. Порядок — по отдаче на вложенное время.

| Книга | Зачем | Когда |
|---|---|---|
| **Google SRE Book** и **SRE Workbook** — [бесплатно на sre.google](https://sre.google/books/) | Разделы про SLO, error budget и on-call. Это ровно тот словарь, которого не хватает при опыте дежурств: три вечера превращают «сидел на поддержке 24/7» в «владел надёжностью с измеримым SLO» | **Первое. Максимальная отдача из всего списка** |
| **The Kubernetes Book**, Nigel Poulton | Самая быстрая нормальная книга по K8s, обновляется ежегодно | После первого своего кластера |
| **Terraform: Up & Running**, Yevgeniy Brikman | Как писать Terraform, чтобы не было больно через год | После первого своего модуля |
| **Kubernetes Up & Running** | Академичнее Poulton, лучше про архитектуру | Если хочется глубже |
| **Accelerate** (DORA) | Откуда взялись четыре метрики, которые спрашивают на платформенных вакансиях | Перед собеседованиями на Platform Engineer |
| **The Phoenix Project** | Художественная, про то, зачем всё это. Хороша именно когда бросаешь: возвращает смысл | В момент, когда «опять забросил» |
| **How Linux Works** · [The Linux Command Line](https://linuxcommand.org/tlcl.php) (бесплатно) | Если решишь добирать основы — точечно отсюда, а не с начала | По потребности |
| **Systems Performance**, Brendan Gregg | Тяжёлая. Тот уровень, после которого вопросы про диагностику перестают существовать | Когда закроешь всё остальное |

---

## Документацию всё-таки читать

Это не «для справки». Половина лучших текстов в индустрии — официальная документация.

- [kubernetes.io → Concepts](https://kubernetes.io/docs/concepts/) — **целиком.** Лучший текст по Kubernetes, который существует.
- [ArgoCD → Core Concepts и Best Practices](https://argo-cd.readthedocs.io/en/stable/) — короткие, закрывают весь GitOps-минимум.
- [Prometheus → типы метрик и PromQL](https://prometheus.io/docs/prometheus/latest/querying/basics/)
- [Terraform → Language](https://developer.hashicorp.com/terraform/language) — весь.
- [Julia Evans](https://jvns.ca/) — лучшие в мире объяснения Linux, сетей и отладки. Её комиксы про strace, tcpdump и DNS дают понимание, которого не даёт документация.

---

## Рассылки: держать актуальность без усилий

Десять минут в неделю.

- [KubeWeekly](https://www.cncf.io/kubeweekly/) — от CNCF, что произошло в экосистеме
- [SRE Weekly](https://sreweekly.com/) — **разборы реальных публичных аварий.** Самая полезная в списке: чужие постмортемы дают опыт без своих аварий
- [Last Week in AWS](https://www.lastweekinaws.com/) — Corey Quinn, ещё и смешно
- [DevOps Weekly](https://www.devopsweekly.com/)

---

## Сертификация

**CKA — единственная, которая нужна.** С непрофильным образованием формальный сертификат снимает вопрос «откуда он это знает» на уровне HR-фильтра, а экзамен практический, поэтому подготовка совпадает с навыком.

- Программа: [cncf/curriculum](https://github.com/cncf/curriculum)
- Мок-экзамены с таймером: [CK-X](https://github.com/sailor-sh/CK-X)
- Скорость с kubectl: [CKAD-exercises](https://github.com/dgkanatsios/CKAD-exercises), Killercoda
- **Купоны:** [linux-foundation-coupon](https://github.com/techiescamp/linux-foundation-coupon) — часто на 40–50% дешевле. Не покупать по полной цене
- **CKS** — потом, когда будет работа. С банковским профилем это сильный долгосрочный вектор: [kubernetes-goat](https://github.com/madhuakula/kubernetes-goat), [cks](https://github.com/ViktorUJ/cks)

Terraform Associate и AWS SAA не нужны: дешевле показать проект.

---

## Чего не надо

Не менее полезно, чем список того, что брать — потому что распыление здесь главный риск.

- **Не учить все инструменты подряд.** В CNCF Landscape полторы тысячи проектов. Знать надо один из категории и понимать, зачем категория существует. «Знаю Argo и понимаю, чем от него отличается Flux» — сильный ответ; «слышал про десять инструментов» — слабый.
- **Не учить Jenkins с нуля**, если его нет в вакансии. Легаси, порог входа высокий, отдача низкая.
- **Не начинать с service mesh.** Istio — самая частая ловушка «выучил сложное, не зная простого». К нему приходят, когда есть боль.
- **Не учить Go специально ради DevOps.** Читать Go полезно, писать — только если целишься в разработку операторов. Bash и Python закрывают 95% задач.
- **Не сдавать несколько сертификатов подряд.** Один CKA закрывает вопрос; три выглядят как замена практике.
- **Не читать три курса по одной теме.**
- **Не покупать курс, чтобы почувствовать, что начал.** Покупка — не начало. Начало — это первая задача, сделанная руками.
