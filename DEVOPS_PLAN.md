# План выхода на DevOps / SRE / Platform Engineer

**Версия 2.** Составлено на основе анализа всех ~546 starred-репозиториев профиля [@nurekella](https://github.com/nurekella?tab=stars) и разбора актуального резюме.
Срок: 8 недель, 11 августа — 5 октября 2026. Целевые роли: **DevOps Engineer, SRE, Platform Engineer**.

> **Что изменилось от версии 1.** Первая версия строилась на README этого репозитория, где текущим местом работы указан Kaspi Bank. Резюме от 15 июля 2026 показало другую картину: Kubernetes, Terraform, Ansible, GitLab CI, Yandex Cloud и Proxmox уже в работе, плюс два года руководства управлением IT-инфраструктуры в банке. Диагноз «нет Kubernetes, нет Terraform — это блокеры» был неверен и снят. План переписан: меньше изучения основ, больше глубины, портфолио и умения об этом говорить.

---

## 1. Диагностика

### Что уже есть

| Направление | Где и сколько |
|---|---|
| **Kubernetes** | Alif Islamic Bank — развёртывание и настройка кластеров |
| **Terraform** | Alif — провижининг серверов |
| **Ansible** | Alif, Товарная биржа Alan — конфигурация и обновления серверов |
| **GitLab CI** | Alif — пайплайны CI/CD |
| **Облака** | Yandex Cloud, PrimeCloud, PS Cloud, on-premise Proxmox |
| **Мониторинг и логи** | Prometheus, Grafana, Zabbix, Grafana Loki, Graylog, Wazuh, ELK — четыре места работы |
| **Базы** | PostgreSQL, MS SQL Server |
| **Сети и доступы** | FortiGate и FortiGate VDOM, WireGuard, FreeIPA как LDAP, Cisco |
| **Виртуализация** | Proxmox, VMware ESXi, Hyper-V |
| **Руководство** | 2 года — руководитель управления IT-инфраструктуры и операций |
| **Отрасль** | 8 лет из 10 в финансовом секторе: банки, товарная биржа, доступность 24/7 |
| **Языки** | Казахский родной, русский C2, английский B2 |

Это профиль **middle+ / senior инфраструктурного инженера**, а не начинающего DevOps. Изучать с нуля почти нечего.

### Что реально мешает

| # | Проблема | Суть | Приоритет |
|---|---|---|---|
| 1 | **Позиционирование в резюме** | Желаемая должность «Системный инженер», Kubernetes отсутствует в тегах навыков, Terraform и K8s описаны однострочниками. Тебя не находят по запросу «DevOps». | 🔴 главный рычаг |
| 2 | **Портфолио** | В GitHub-профиле только README с устаревшим резюме. Показать Kubernetes и IaC вне слов нечем. | 🔴 высокий |
| 3 | **Kubernetes: эксплуатация, а не установка** | Кластер поднять умеешь. Спрашивают другое: probes, requests/limits и QoS, RBAC, scheduling, разбор CrashLoopBackOff и Pending, rolling update без простоя. | 🔴 высокий |
| 4 | **Helm и GitOps** | Ни Helm, ни ArgoCD в резюме нет. Спрашивают сразу после базового Kubernetes, это стандарт деплоя. | 🟠 высокий |
| 5 | **SRE-словарь** | Практика есть — дежурства 24/7, инциденты, Prometheus четыре года. Терминов нет: SLI, SLO, error budget, toil, blameless postmortem. На собеседовании SRE это половина разговора. | 🟠 быстро закрыть |
| 6 | **PromQL** | Prometheus давно, но запрос на собеседовании пишут с нуля: `rate`, `increase`, `histogram_quantile`. | 🟠 средний |
| 7 | **Terraform: state и модули** | Провижинить умеешь. Спрашивают про state в команде, locking, модули, `plan` в CI, дрейф конфигурации. | 🟠 средний |
| 8 | **Platform Engineering** | Целевая роль. Ты фактически строишь платформу для команд разработки, но не говоришь на этом языке: self-service, developer experience, Backstage, Gateway API. | 🟠 средний |
| 9 | **Артикуляция** | Самое недооценённое. Ты делаешь больше, чем можешь внятно рассказать. «Настроил кластер» вместо истории с масштабом, решением и результатом. | 🔴 высокий |
| 10 | **CKA** | Образование непрофильное — магистр экономики, бакалавр по транспорту. Формальный сертификат снимает вопрос «откуда он это знает» на уровне HR-фильтра. | 🟠 к концу октября |

### Проблема со звёздами

546 звёзд — склад, а не план. Около 70% — self-hosted приложения, файловые менеджеры, PDF-инструменты, iOS-твики. Релевантных примерно 60, и они тонут в шуме. Главный риск плана — распыление, а не нехватка материала. **Остальные 480 не открывать до оффера.**

---

## 2. Стратегия

Веса треков изменены относительно версии 1: базы учить почти не надо, поэтому практики меньше, а артикуляции и портфолио больше.

```
┌──────────────────────────────────────────────────────────────────┐
│  A — ПРАКТИКА · 60 мин/день                                      │
│      Глубина там, где спрашивают. Не основы.                     │
├──────────────────────────────────────────────────────────────────┤
│  B — АРТИКУЛЯЦИЯ · 40 мин/день                                   │
│      Вопросы вслух + истории по STAR из своего опыта.            │
│      Главный недооценённый трек.                                 │
├──────────────────────────────────────────────────────────────────┤
│  C — ПОРТФОЛИО · 3–4 ч в выходной                                │
│      4 проекта. Единственный способ показать навык до звонка.    │
├──────────────────────────────────────────────────────────────────┤
│  D — ПОИСК · 30 мин в пятницу                                    │
│      Отклики, письма, ретро по вопросам с собеседований.         │
└──────────────────────────────────────────────────────────────────┘
```

Бюджет: ~17 часов в неделю, ~135 часов за восемь недель.

**Правило одного источника:** на тему — один основной материал. Остальное только справочник, когда застрял.

---

## 3. Неделя 0 — до 11 августа

Самая высокая отдача на вложенное время во всём плане — здесь. Правки в резюме дают больше, чем любая неделя учёбы.

**Резюме на hh — 20 минут:**
1. Желаемая должность → **DevOps Engineer**; специализации → DevOps-инженер / SRE / Системный инженер
2. **Kubernetes в теги навыков** (сейчас его там нет) + переписать блок навыков целиком
3. Указать зарплату
4. Формат работы → в офисе, гибрид, удалённо

**Резюме — на этой неделе:**
5. Пометки о совмещении: B2M, Alan, Improvado, Ниет — «частичная занятость, совмещение»
6. Переписать блок Alif Bank: IaC, Kubernetes и CI/CD первыми пунктами, со цифрами
7. Раскрыть Improvado, сократить блоки 2015–2020
8. Обновить README этого репозитория — он показывает Kaspi Bank как текущее место работы четвёртый год

**Стенд:**
- Кластер: [k3d](https://github.com/k3d-io/k3d) локально или [k3s](https://github.com/k3s-io/k3s) на VM; альтернатива — [k0s](https://github.com/k0sproject/k0s)
- [k9s](https://github.com/derailed/k9s) — терминальный дашборд, must-have
- [kubectx](https://github.com/ahmetb/kubectx) / [kubeswitch](https://github.com/danielfoehrKn/kubeswitch), [netshoot](https://github.com/nicolaka/netshoot), [kubernetes-toolkit](https://github.com/swade1987/kubernetes-toolkit)
- helm, terraform или [opentofu](https://github.com/opentofu/opentofu), argocd CLI

**Поиск:**
- 4 пустых публичных репозитория под проекты
- Начать откликаться. 5–10 вакансий в неделю с этого момента, не «когда буду готов»

---

## 4. Недели 1–8

### Неделя 1 (11–17 авг) · Kubernetes: эксплуатация вместо установки

Ты умеешь ставить кластер. Собеседуют по тому, что происходит после.

**Основной источник:** [omerbsezer/Fast-Kubernetes](https://github.com/omerbsezer/Fast-Kubernetes) — проходить не подряд, а точечно по темам ниже. Сверка полноты: [techiescamp/kubernetes-learning-path](https://github.com/techiescamp/kubernetes-learning-path).

- Probes: liveness / readiness / startup — что сломается, если перепутать
- Resources: requests vs limits, QoS-классы, OOMKilled, кого убьют первым
- RBAC: ServiceAccount, Role, RoleBinding, ClusterRole — минимальные права на практике
- Scheduling: nodeSelector, affinity и anti-affinity, taints и tolerations, topology spread
- Rolling update без простоя: maxSurge, maxUnavailable, PDB
- Deployment vs StatefulSet vs DaemonSet — когда что и почему
- Troubleshooting: разобрать своими руками CrashLoopBackOff, ImagePullBackOff, Pending, Evicted

**Практика:** [Manoj-engineer/k8squest](https://github.com/Manoj-engineer/k8squest) — задачи на troubleshooting, ровно формат живого собеседования. Плюс [natrontech/kubelab](https://github.com/natrontech/kubelab).

**Инструменты:** [kube-linter](https://github.com/stackrox/kube-linter), [kor](https://github.com/yonahd/kor), [krr](https://github.com/robusta-dev/krr) — рекомендации по ресурсам, готовый ответ на «как вы подбираете limits».

---

### Неделя 2 (18–24 авг) · Kubernetes: внутренности + Helm

Это неделя, которая отличает «настроил по гайду» от «понимаю, что происходит».

- [jamiehannaford/what-happens-when-k8s](https://github.com/jamiehannaford/what-happens-when-k8s) — прочитать полностью и уметь рассказать. Прямой вопрос на собеседовании.
- [kelseyhightower/kubernetes-the-hard-way](https://github.com/kelseyhightower/kubernetes-the-hard-way) — кластер вручную, компонент за компонентом. Один-два дня. **Не пропускать:** ты ставил кластеры инструментами, это даёт слой под ними.
- NetworkPolicy на практике; [cilium](https://github.com/cilium/cilium) — что такое eBPF и зачем, базово
- **Helm:** свой чарт с нуля — values, templates, helpers, зависимости, hooks. [chart-testing](https://github.com/helm/chart-testing) для линта, [helmfile](https://github.com/helmfile/helmfile) для множества релизов
- Диагностика трафика: [ksniff](https://github.com/eldadru/ksniff), [kubeshark](https://github.com/kubeshark/kubeshark), [inspektor-gadget](https://github.com/inspektor-gadget/inspektor-gadget)

---

### Неделя 3 (25–31 авг) · GitOps

Этого в резюме нет вообще, а спрашивают почти всегда после Kubernetes.

- ArgoCD в свой кластер: приложение из Git, App-of-Apps, синхронизация, self-heal, rollback
- [cloudogu/gitops-patterns](https://github.com/cloudogu/gitops-patterns) — паттерны и антипаттерны процесса, читать обязательно
- Окружения и продвижение релизов dev→stage→prod: [akuity/kargo](https://github.com/akuity/kargo)
- Проверки до кластера: [zapier/kubechecks](https://github.com/zapier/kubechecks)
- **Секреты в Git** — обязательный вопрос: SOPS через [sops-secrets-operator](https://github.com/isindir/sops-secrets-operator), либо [Infisical](https://github.com/Infisical/infisical), либо Vault → [vault-kubernetes-kms](https://github.com/FalcoSuessgott/vault-kubernetes-kms)
- Policy as code: [kyverno](https://github.com/kyverno/kyverno) + Pod Security Standards
- Альтернативы для контекста: [pipecd](https://github.com/pipe-cd/pipecd), [werf/nelm](https://github.com/werf/nelm), [kluctl](https://github.com/kluctl/kluctl)

---

### Неделя 4 (1–7 сен) · Observability и SRE

Твоя сильная сторона — здесь она переводится на язык, которым спрашивают.

- **PromQL** — главное за неделю. [acend/prometheus-training](https://github.com/acend/prometheus-training): `rate`, `irate`, `increase`, `histogram_quantile`, агрегации; разница counter / gauge / histogram / summary
- Алерты: [samber/awesome-prometheus-alerts](https://github.com/samber/awesome-prometheus-alerts) — растащить в свой проект
- Дашборды: [dotdc/grafana-dashboards-kubernetes](https://github.com/dotdc/grafana-dashboards-kubernetes)
- Логи: [Loki](https://github.com/grafana/loki) — у тебя есть и Loki, и ELK, и Graylog; уметь сравнить и обосновать выбор
- Пробы извне: [blackbox_exporter](https://github.com/prometheus/blackbox_exporter), [ssl_exporter](https://github.com/ribbybibby/ssl_exporter)
- Трейсинг базово: OpenTelemetry; поставить [signoz](https://github.com/SigNoz/signoz) или [coroot](https://github.com/coroot/coroot)
- **SRE-словарь** — [dastergon/awesome-sre](https://github.com/dastergon/awesome-sre): SLI, SLO, SLA, error budget, toil, MTTR и MTBF, blameless postmortem, on-call rotation. Два вечера чтения, после которых твои четыре года дежурств начинают звучать как SRE-опыт, а не как «сидел на телефоне»
- Инциденты: [keep](https://github.com/keephq/keep), [Grafana OnCall](https://github.com/grafana-cold-storage/oncall), [gatus](https://github.com/TwiN/gatus)

---

### Неделя 5 (8–14 сен) · Terraform и CI/CD — глубина

Не основы. Только то, о чём спрашивают и что отличает «применял» от «владею».

**Terraform:**
- **State:** remote backend, locking, что делать при потере, `import`, `state mv`, дрейф конфигурации после ручных правок в консоли
- Модули: свой переиспользуемый, версионирование, [terraform-docs](https://github.com/terraform-docs/terraform-docs)
- Окружения: workspaces против отдельных каталогов, и почему второе обычно лучше
- `plan` в CI и review плана как процесс: [runatlantis/atlantis](https://github.com/runatlantis/atlantis)
- Контекст: [opentofu](https://github.com/opentofu/opentofu) — что за форк и почему; [stategraph](https://github.com/stategraph/stategraph)
- Best practices: [brikis98/terraform-up-and-running](https://github.com/brikis98/terraform-up-and-running) — разобрать примеры модулей
- Приватный registry: [terrareg](https://github.com/MatthewJohn/terrareg)

**CI/CD — второй пайплайн к твоему GitLab CI:**
- GitHub Actions: [nektos/act](https://github.com/nektos/act) для локального прогона, [zizmor](https://github.com/zizmorcore/zizmor) для безопасности workflow
- Разобрать построчно [cicd-excellence/app](https://github.com/cicd-excellence/app) + [infra](https://github.com/cicd-excellence/infra) — шаблон для флагманского проекта
- Self-hosted runners в K8s: [actions-runner-controller](https://github.com/actions/actions-runner-controller) — сильный пункт в резюме
- GitLab CI глубже: DAG через `needs`, `rules`, cache, matrix, `include` и шаблоны, environments. Локально — [gitlab-ci-local](https://github.com/firecow/gitlab-ci-local)

---

### Неделя 6 (15–21 сен) · Platform Engineering

Целевая роль, которой в первой версии плана не было. Здесь твой опыт из Alif читается лучше всего.

- **Идея платформы:** внутренняя платформа как продукт для команд разработки; self-service вместо тикетов; golden path
- [backstage/backstage](https://github.com/backstage/backstage) — поставить, собрать каталог сервисов, шаблон нового сервиса. Это де-факто стандарт developer portal
- Абстракции над Kubernetes: [score-spec](https://github.com/score-spec/spec), [radius](https://github.com/radius-project/radius), [cyclops](https://github.com/cyclops-ui/cyclops), [kro](https://github.com/kubernetes-sigs/kro)
- Ingress и Gateway API: [nginx-gateway-fabric](https://github.com/nginx/nginx-gateway-fabric), [kgateway](https://github.com/kgateway-dev/kgateway), миграция с ingress-nginx — [ingress-migration-kit](https://github.com/ubermorgenland/ingress-migration-kit)
- Автоскейлинг и эффективность: [keda](https://github.com/kedacore/keda), [karpenter](https://github.com/aws/karpenter-provider-aws), [kueue](https://github.com/kubernetes-sigs/kueue), [zeropod](https://github.com/ctrox/zeropod)
- **FinOps** — на платформенных вакансиях спрашивают про стоимость: [wozz](https://github.com/WozzHQ/wozz), [krr](https://github.com/robusta-dev/krr), [aws-finops-dashboard](https://github.com/ravikiranvm/aws-finops-dashboard)
- Базы в Kubernetes: [cloudnative-pg](https://github.com/cloudnative-pg/cloudnative-pg) — при твоём опыте с PostgreSQL это быстрый и сильный пункт
- Мультикластер: [clusternet](https://github.com/clusternet/clusternet), [k3k](https://github.com/rancher/k3k), [cozystack](https://github.com/cozystack/cozystack)

---

### Неделя 7 (22–28 сен) · Security в Kubernetes + портфолио-интенсив

Банковский бэкграунд плюс FortiGate и FreeIPA — DevSecOps твоё естественное продолжение, и это отличает тебя от кандидатов из продуктовых компаний.

- [madhuakula/kubernetes-goat](https://github.com/madhuakula/kubernetes-goat) — уязвимый по дизайну кластер. Пройти несколько сценариев: лучший способ понять K8s security и получить живые истории для собеседования
- [trivy](https://github.com/aquasecurity/trivy) и [SecretScanner](https://github.com/deepfence/SecretScanner) в пайплайн
- Kyverno-политики в проекте, [kubearmor](https://github.com/kubearmor/KubeArmor) для рантайма
- [Swordfish-Security/awesome-devsecops-russia](https://github.com/Swordfish-Security/awesome-devsecops-russia) — на русском
- Supply chain: [Software-Supply-Chain-Security](https://github.com/vishalgarg-sec/Software-Supply-Chain-Security); аудит: [lynis](https://github.com/CISOfy/lynis), [Gixy-Next](https://github.com/MegaManSec/Gixy-Next) для nginx
- Доступы для контекста: [teleport](https://github.com/gravitational/teleport), [pomerium](https://github.com/pomerium/pomerium), [keycloak](https://github.com/keycloak/keycloak), [authentik](https://github.com/goauthentik/authentik)

**Вторая половина недели — доводка всех четырёх проектов и README к каждому.**

---

### Неделя 8 (29 сен — 5 окт) · CKA и интенсив собеседований

Новых тем нет.

- Мок-экзамены с таймером: [sailor-sh/CK-X](https://github.com/sailor-sh/CK-X) — несколько прогонов
- Скорость с kubectl: [dgkanatsios/CKAD-exercises](https://github.com/dgkanatsios/CKAD-exercises)
- Программа: [cncf/curriculum](https://github.com/cncf/curriculum)
- Прогон всех вопросов трека B вслух, с таймером
- Собеседования каждый день

---

## 5. Трек B — артикуляция

Самый недооценённый трек. Ты делаешь больше, чем можешь внятно рассказать — это и есть разрыв между твоим настоящим уровнем и тем, как он читается.

**Метод:** 20 вопросов в день вслух по [bregman-arie/devops-exercises](https://github.com/bregman-arie/devops-exercises), потом сверка. Не глазами — на собеседовании ты говоришь.

**Банки вопросов:**

| Репозиторий | Что даёт |
|---|---|
| [bregman-arie/devops-exercises](https://github.com/bregman-arie/devops-exercises) | Основной тренажёр, все темы |
| [rmntrvn/adm_linux_ops_questions](https://github.com/rmntrvn/adm_linux_ops_questions) | **На русском** — близко к рынку КЗ и РФ |
| [moabukar/tech-vault](https://github.com/moabukar/tech-vault) | Вопросы + практические челленджи |
| [Swfuse/devops-interview](https://github.com/Swfuse/devops-interview) | DevOps и системное администрирование |
| [trimstray/test-your-sysadmin-skills](https://github.com/trimstray/test-your-sysadmin-skills) | 284 вопроса по Linux — проверка глубины |
| [NotHarshhaa/into-the-devops](https://github.com/NotHarshhaa/into-the-devops) | Разбор по темам |
| [ByteByteGoHq/system-design-101](https://github.com/ByteByteGoHq/system-design-101) | Архитектурные вопросы, картинками |
| [alex/what-happens-when](https://github.com/alex/what-happens-when) | Классика: что происходит при вводе google.com |

Шпаргалки перед собеседованием: [devops-cheatsheet](https://github.com/NotHarshhaa/devops-cheatsheet), [git-cheat-sheet](https://github.com/arslanbilal/git-cheat-sheet), [awesome-cheatsheets](https://github.com/LeCoupa/awesome-cheatsheets).

### Истории по STAR — вот это надо готовить первым

У тебя редкий по нынешним временам материал: реальный прод банка, дежурства 24/7, инциденты, миграции, руководство командой. Большинство кандидатов рассказывают про домашние лабы. Подготовь письменно 6 историй по схеме «ситуация → задача → что сделал → результат»:

1. Самый серьёзный инцидент, который разбирал. Что упало, как локализовал, чем починил, что изменил потом, чтобы не повторилось
2. Что автоматизировал через Ansible или Terraform, и сколько времени это сэкономило
3. Как строил CI/CD в GitLab CI: что было до, что стало, сколько занимает релиз теперь
4. Зачем понадобился Kubernetes и что он изменил
5. Случай, когда сломал прод: как чинил и какие выводы
6. Как руководил командой: что поменял в процессах, найме, дежурствах

### Вопросы, которые спросят почти наверняка

**Kubernetes**
- Опиши архитектуру кластера. За что отвечает каждый компонент?
- Что происходит по шагам при `kubectl apply -f deployment.yaml`?
- Pod в CrashLoopBackOff — действия по шагам? В Pending — причины?
- Liveness vs readiness vs startup. Что сломается, если перепутать?
- requests vs limits, QoS-классы. Кого убьют первым при нехватке памяти?
- Обновление без простоя: rolling update, maxSurge, maxUnavailable, PDB
- Service ClusterIP — как трафик доходит до Pod?
- Deployment vs StatefulSet — когда нужен второй?
- Как правильно хранить секреты? *(Secret в etcd — это base64, а не шифрование)*

**GitOps и Helm**
- Что такое GitOps и чем отличается от «CI деплоит через kubectl»?
- Как ArgoCD понимает, что состояние разошлось? Что такое self-heal и drift?
- Как хранить секреты в Git-репозитории?
- Helm: что такое release, чем `upgrade` отличается от `apply`, как откатиться?

**Terraform**
- Зачем state и что будет, если его потерять? Как работать с ним в команде?
- Что делать, если ресурс поменяли руками в консоли?
- `import` — зачем? Как не хранить пароли в `.tf`?

**SRE и мониторинг**
- Pull vs push. Почему Prometheus — pull?
- Counter vs gauge vs histogram. Напиши запрос: доля ошибок 5xx за 5 минут
- SLI, SLO, error budget — что это и как считается?
- Как строишь алертинг, чтобы не было alert fatigue?
- Сервис лёг. Действия в первые пять минут?

**Linux и сети**
- SIGTERM vs SIGKILL. `df` показывает 100%, `du` — 50%, почему?
- Как найти, что съело диск, память, CPU? Пошагово
- Что происходит при загрузке от BIOS до shell?
- Как посмотреть, какой процесс слушает порт?

**Docker**
- Namespaces и cgroups. Контейнер vs VM
- COPY vs ADD, CMD vs ENTRYPOINT
- Как уменьшить образ? Почему нельзя запускать от root?

**Git и CI/CD**
- merge vs rebase, когда что. `revert` vs `reset --hard` vs `reset --soft`
- Опиши свой пайплайн от коммита до прода
- Blue-green vs canary vs rolling — что выберешь и почему?

**Platform Engineering**
- Что такое внутренняя платформа и зачем она, если есть Kubernetes?
- Что такое golden path и self-service для разработчиков?
- Как измерить, что платформа полезна? *(DORA-метрики: частота деплоя, lead time, MTTR, доля неудачных изменений)*

---

## 6. Трек C — четыре проекта

В GitHub-профиле сейчас нет ничего, кроме README. Каждый проект — отдельный публичный репозиторий с подробным README, схемой и скриншотами. Проекты подобраны под целевые роли и опираются на то, что ты уже умеешь, — это не учебные лабы, а витрина.

### 1. `k8s-production-stack` · недели 1–2
Приложение в Kubernetes так, как это делают в проде.
- Свой Helm-чарт: deployment, service, ingress, configmap, secret, HPA, PDB
- Probes настроены осознанно, requests и limits с обоснованием откуда цифры
- NetworkPolicy, RBAC с минимальными правами, отдельный ServiceAccount, non-root
- kube-linter и trivy в проверках
- Раздел README **«Troubleshooting»**: какие проблемы ловил и как решил — это читают внимательнее всего

### 2. `gitops-platform` · недели 3–4 · **флагман**
Полный путь от коммита до прода. Показываешь первым.
- Два репозитория — приложение и инфраструктура, по образцу cicd-excellence
- CI: тесты → сборка → trivy → push в registry → bump тега в infra-репо
- CD: ArgoCD, App-of-Apps, три окружения
- Секреты через SOPS, политики Kyverno
- Схема архитектуры в README
- **Демонстрация rollback:** сломать релиз, откатить, приложить лог

### 3. `terraform-platform-modules` · неделя 5
IaC как это выглядит у зрелой команды.
- Модули network / compute / k8s, remote state с locking, окружения dev и prod
- Ansible-роли для базовой настройки и харденинга
- CI: `fmt` → `validate` → `tflint` → `plan` на PR → `apply` на merge
- terraform-docs для автодокументации
- LocalStack, [ministack](https://github.com/ministackorg/ministack) или Hetzner за 5–10 € в месяц

### 4. `observability-stack` · недели 6–7
Играет на твоей сильнейшей стороне и закрывает SRE-вакансии.
- Prometheus, Grafana, Loki, alertmanager в Kubernetes через Helm
- Свои PromQL-запросы и алерты, не только готовые дашборды
- **Дашборд SLO с error budget** — именно это отличает «мониторинг» от SRE
- Blackbox и ssl_exporter, трейсинг через OpenTelemetry
- README с разбором: какие алерты шумели и как чинил

Идеи для дополнительных: [NotHarshhaa/DevOps-Projects](https://github.com/NotHarshhaa/DevOps-Projects).

---

## 7. Сертификация

**CKA — единственная, которая нужна.** С непрофильным образованием формальный сертификат снимает вопрос «откуда он это знает» на уровне HR-фильтра, а экзамен практический, так что подготовка совпадает с навыком.

- Цель: конец октября, после недели 8
- Программа: [cncf/curriculum](https://github.com/cncf/curriculum) · Моки: [CK-X](https://github.com/sailor-sh/CK-X) · Скорость: [CKAD-exercises](https://github.com/dgkanatsios/CKAD-exercises)
- **Купоны:** [techiescamp/linux-foundation-coupon](https://github.com/techiescamp/linux-foundation-coupon) — часто на 40–50% дешевле, не покупай по полной цене
- Бейджи в профиль: [Free-Credly-Badges](https://github.com/CloudNativeStudyGroup/Free-Credly-Badges)
- **CKS** — потом, когда будет работа. С банковским профилем это сильный долгосрочный вектор: [kubernetes-goat](https://github.com/madhuakula/kubernetes-goat), [cks](https://github.com/ViktorUJ/cks), [kcsa-mock](https://github.com/thiago4he/kubernetes-security-kcsa-mock)
- Terraform Associate и AWS SAA — не нужны, дешевле показать проект

---

## 8. Рутина

**Рабочий день — 1 ч 40 мин**
```
40 мин   Трек B — 20 вопросов вслух или одна история по STAR письменно
60 мин   Трек A — тема недели, руками в кластере
```

**Выходной — 3–4 часа**
```
3 ч      Трек C — проект
1 ч      Повторение вопросов, где плыл
```

**Пятница — 30 минут, трек D**
- Что из недели не закрыл? Переносим или выкидываем?
- Сколько откликов, сколько собеседований?
- **Что спросили, чего я не знал?** → в план приоритетно, поверх всего остального

---

## 9. Правила

1. **Не открывай остальные 480 звёзд до оффера.** Главный риск — распыление, а не нехватка материала.
2. **Один источник на тему.** Начал Fast-Kubernetes — не переключайся на третий день.
3. **Руками, а не глазами.** Просмотренный туториал не равен навыку.
4. **Резюме важнее учёбы на первой неделе.** Правки в hh дают больше отдачи, чем любая изученная тема: тебя перестают отсеивать до прочтения.
5. **Ты уже сильнее, чем твоё резюме.** Задача плана — не догнать рынок, а перестать себя недопродавать. Kubernetes, Terraform, GitLab CI, облака, руководство командой, банковский прод, 24/7 — это уже есть.
6. **Собеседования параллельно.** Каждое возвращает точный список пробелов — точнее любого плана.

---

## 10. Контрольные точки

| Дата | Состояние |
|---|---|
| **11 авг** | Резюме на hh переписано, откликов пошло, стенд работает, 4 репозитория созданы |
| 17 авг | Kubernetes-эксплуатация: уверенно про probes, QoS, RBAC, troubleshooting. Проект 1 в работе |
| 31 авг | the-hard-way пройден, свой Helm-чарт, ArgoCD в кластере. Проекты 1–2 готовы |
| 14 сен | SRE-словарь и PromQL, Terraform-глубина, второй пайплайн. Проект 3 готов |
| 28 сен | Platform-темы, K8s security, проект 4 готов, 400+ вопросов пройдено |
| 5 окт | Моки CKA сданы, четыре проекта отполированы, идут финальные этапы собеседований |
| конец окт | CKA |

Если точка не закрыта — не двигай дату, а сокращай объём следующей недели. Сдвиг дат обычно означает конец плана.

---

*План обновляется каждую пятницу по итогам ретро и по вопросам с реальных собеседований. Живой план обгоняет правильный.*
