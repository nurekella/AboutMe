# План освоения DevOps и подготовки к собеседованиям

**Составлено на основе анализа всех ~546 starred-репозиториев аккаунта [@nurekella](https://github.com/nurekella?tab=stars)**
Дата: 10 августа 2026 · Срок плана: 8 недель (11 августа — 5 октября 2026)
Цель: выйти на рынок как **DevOps Engineer (Middle/Middle+)** с подтверждённой практикой в Kubernetes, IaC и CI/CD.

---

## 0. Диагностика: где ты сейчас

### Что у тебя уже есть (по резюме) — это твой козырь, не обесценивай
| Навык | Уровень | Где применял |
|---|---|---|
| CI/CD в Jenkins | **боевой, 4+ года** | Kaspi Bank — сборка и деплой |
| Docker | боевой | Kaspi + Al Hilal |
| Мониторинг: Prometheus, Grafana, Zabbix | боевой | Kaspi, Al Hilal |
| Логи: ELK | боевой | Kaspi |
| Linux/Windows администрирование | **сильный, 9 лет** | все места работы |
| Сети: маршрутизация, DNS, DHCP, VLAN, Cisco | сильный | Al Hilal |
| Виртуализация: VMware ESXi, Hyper-V | сильный | Al Hilal |
| Балансировка нагрузки | практика | Kaspi |
| Базы: MS SQL | базовый | Kaspi |
| Backup: Veeam | практика | Al Hilal |
| Дежурство 24/7, инциденты | боевой | Kaspi |

**Вывод:** у тебя профиль классического «инфраструктурного» DevOps из банка. Это ценно — банковский опыт, продакшн, 24/7. Тебя НЕ надо учить с нуля.

### Критические пробелы — именно из-за них тебя срезают на собеседованиях
Отсортировано по важности для рынка вакансий DevOps в 2026:

| # | Пробел | Почему критично | Приоритет |
|---|---|---|---|
| 1 | **Kubernetes** | В резюме его нет вообще. 90% вакансий DevOps сегодня = K8s. Это единственная главная причина отказов. | 🔴 БЛОКЕР |
| 2 | **Terraform / IaC** | Второй по частоте пункт в вакансиях. «Руками в vSphere» больше не продаётся. | 🔴 БЛОКЕР |
| 3 | **GitLab CI / GitHub Actions** | Jenkins — это хорошо, но его считают легаси. Нужен YAML-пайплайн. | 🔴 высокий |
| 4 | **Ansible** | Ожидается по умолчанию от любого, кто трогал серверы. | 🟠 высокий |
| 5 | **Облако (AWS или Yandex Cloud)** | Хотя бы понимание VPC/IAM/EC2/S3/EKS и умение говорить на этом языке. | 🟠 высокий |
| 6 | **GitOps (ArgoCD / Flux) + Helm** | Стандарт деплоя в K8s. Спрашивают почти всегда после базового K8s. | 🟠 средний |
| 7 | **Bash + Python скриптинг** | На собесе дают писать скрипт. Нужна уверенность. | 🟠 средний |
| 8 | **Git на уровне «объясни rebase vs merge»** | Спрашивают в 100% случаев, отвечают плохо в 50%. | 🟡 быстро закрыть |
| 9 | **Публичное портфолио** | Твой GitHub сейчас = только README с резюме. Нужны 3–4 живых проекта. | 🟠 высокий |

### Проблема с твоими звёздами (честно)
546 звёзд — это **склад, а не план**. Там ~70% self-hosted-приложений, iOS-твиков, файловых менеджеров и PDF-инструментов, которые не имеют отношения к трудоустройству. Настоящих учебных материалов по DevOps — примерно **60 репозиториев**, и они тонут в шуме.

Ниже я вытащил именно их и разложил по неделям. **Всё остальное из звёзд — не открывать до момента, когда получишь оффер.** Это главное правило плана.

---

## 1. Стратегия: три параллельных трека

Учиться «по темам последовательно» — медленно. Работу искать надо сейчас, значит идём тремя треками одновременно, каждый день:

```
┌─────────────────────────────────────────────────────────────┐
│  ТРЕК A — ПРАКТИКА (90 мин/день)                            │
│  Руками в кластере. Главный трек. Даёт навык.               │
├─────────────────────────────────────────────────────────────┤
│  ТРЕК B — СОБЕСЕДОВАНИЯ (30 мин/день)                       │
│  Вопросы-ответы вслух. Даёт оффер. Начинаем с 1-го дня,     │
│  не «когда всё выучу».                                      │
├─────────────────────────────────────────────────────────────┤
│  ТРЕК C — ПОРТФОЛИО (выходные, 3–4 ч)                       │
│  4 проекта в GitHub. Даёт доказательство навыка.            │
└─────────────────────────────────────────────────────────────┘
```

**Бюджет времени:** 2 часа в рабочий день + 4 часа в выходной = **~18 часов в неделю**, ~145 часов за 8 недель. Этого достаточно, если не распыляться.

**Правило одного репозитория:** на каждую тему — ОДИН основной источник. Остальные — только справочник, если застрял. Не читать по три курса про Docker.

---

## 2. Неделя 0 — подготовка стенда (2–3 вечера, до 11 августа)

Без своего кластера учить K8s бессмысленно. Собираем окружение один раз.

**Что поднять локально:**
```bash
# 1. Kubernetes локально — k3d (лёгкий, из твоих звёзд)
#    https://github.com/k3d-io/k3d
k3d cluster create learn --agents 2

# 2. Обязательный набор CLI
#    k9s — TUI для кластера (из твоих звёзд, будешь жить в нём)
#    https://github.com/derailed/k9s
#    kubectx/kubens — переключение контекстов
#    https://github.com/ahmetb/kubectx
#    helm, terraform (или opentofu), ansible

# 3. Тренажёр shell — прогревай пальцы
#    https://github.com/iximiuz/shellgym
```

**Репозитории для стенда (все из твоих звёзд):**
- [k3d-io/k3d](https://github.com/k3d-io/k3d) — кластер в Docker, стартовый вариант
- [k3s-io/k3s](https://github.com/k3s-io/k3s) — тот же K8s на VM, когда захочешь «по-настоящему»
- [derailed/k9s](https://github.com/derailed/k9s) — терминальный дашборд, must-have
- [ahmetb/kubectx](https://github.com/ahmetb/kubectx) + [danielfoehrKn/kubeswitch](https://github.com/danielfoehrKn/kubeswitch)
- [swade1987/kubernetes-toolkit](https://github.com/swade1987/kubernetes-toolkit) — контейнер со всем тулингом сразу
- [nicolaka/netshoot](https://github.com/nicolaka/netshoot) — дебаг сети в K8s, пригодится постоянно
- [srl-labs/containerlab](https://github.com/srl-labs/containerlab) — если захочешь потренировать сети отдельно

**Ещё в неделю 0:**
1. Создать в GitHub 4 пустых репозитория под проекты (см. §5) — публичных.
2. Переписать README профиля: добавить блок «Стек» с реальными технологиями (сейчас там только текст резюме, рекрутер не видит навыков).
3. Обновить резюме на hh.kz: вынести Jenkins/Docker/Prometheus/ELK в начало, добавить раздел «Изучаю: Kubernetes, Terraform, Ansible, GitLab CI» — это честно и работает.
4. **Начать откликаться на вакансии уже сейчас.** Первые собеседования = бесплатная диагностика пробелов. Не жди «готовности».

---

## 3. ТРЕК A — практика по неделям

### Неделя 1 (11–17 авг): Linux до уровня собеседования + Docker правильно

Ты знаешь Linux, но собеседуют по конкретным вещам: процессы, сигналы, права, systemd, сеть, диагностика.

**Основной источник:**
- [Sagar2366/linux_the_final_boss](https://github.com/Sagar2366/linux_the_final_boss) — 31-дневная программа Linux именно для DevOps. Пройти ускоренно: дни 1–15 за неделю, ориентируясь на разделы, где неуверен.

**Что обязательно уметь к концу недели (проверь себя):**
- `ps`/`top`/`htop`, состояния процессов, зомби, сигналы (SIGTERM vs SIGKILL — спрашивают всегда)
- systemd: unit-файл написать с нуля, `journalctl` с фильтрами
- права: `chmod` в цифрах, SUID/SGID/sticky, umask
- диск: inode, `df` vs `du` расхождение (классический вопрос), LVM
- сеть: `ss`, `ip`, `tcpdump`, маршруты, DNS-резолв по шагам
- диагностика «сервер тормозит»: последовательность действий (load average → CPU/IO/RAM → сеть → логи)

**Docker — довести до продакшн-уровня:**
- [iam-veeramalla/Docker-Zero-to-Hero](https://github.com/iam-veeramalla/Docker-Zero-to-Hero) — основной курс
- [dnaprawa/dockerfile-best-practices](https://github.com/dnaprawa/dockerfile-best-practices) — прочитать целиком, это прямые вопросы на собесе
- [hadolint/hadolint](https://github.com/hadolint/hadolint) — линтер Dockerfile, прогнать свои файлы
- [wagoodman/dive](https://github.com/wagoodman/dive) — посмотреть слои образа, понять почему образ жирный
- [aquasecurity/trivy](https://github.com/aquasecurity/trivy) — сканирование на уязвимости, обязательный ответ на «как обеспечиваете безопасность образов»

**Практика недели:** взять любое приложение, написать multi-stage Dockerfile, уменьшить образ в 5+ раз, прогнать hadolint + trivy, записать результат «до/после». Это готовая история для собеседования.

**Справочники (не читать подряд, только при затыке):**
[mikeroyal/Linux-Guide](https://github.com/mikeroyal/Linux-Guide) · [trimstray/the-book-of-secret-knowledge](https://github.com/trimstray/the-book-of-secret-knowledge) · [chubin/cheat.sh](https://github.com/chubin/cheat.sh) · [LeCoupa/awesome-cheatsheets](https://github.com/LeCoupa/awesome-cheatsheets) · [HariSekhon/DevOps-Bash-tools](https://github.com/HariSekhon/DevOps-Bash-tools)

---

### Неделя 2 (18–24 авг): Kubernetes — база 🔴 самая важная неделя

**Основной источник (выбрать ОДИН как главный):**
- [omerbsezer/Fast-Kubernetes](https://github.com/omerbsezer/Fast-Kubernetes) — **рекомендую как основной.** Структура «тема + лаба», быстро и по делу.
- [iam-veeramalla/Kubernetes-Zero-to-Hero](https://github.com/iam-veeramalla/Kubernetes-Zero-to-Hero) — альтернатива, если Fast-Kubernetes не пойдёт
- [techiescamp/kubernetes-learning-path](https://github.com/techiescamp/kubernetes-learning-path) — как карта: свериться, что ничего не пропустил

**Порядок тем (не отклоняться):**
1. Архитектура: control plane, etcd, api-server, scheduler, controller-manager, kubelet, kube-proxy
2. Pod → ReplicaSet → Deployment (и почему именно так)
3. Service: ClusterIP / NodePort / LoadBalancer, как работает kube-proxy
4. ConfigMap, Secret
5. Namespace, labels, selectors, annotations
6. Probes: liveness / readiness / startup — **спрашивают почти всегда**
7. Resources: requests/limits, QoS-классы, OOMKilled
8. Volumes: PV, PVC, StorageClass
9. StatefulSet vs Deployment vs DaemonSet
10. Ingress + Gateway API (базово)

**Практика:** [Manoj-engineer/k8squest](https://github.com/Manoj-engineer/k8squest) — игра с реальными задачами troubleshooting. Отлично тренирует то, что дают на живом собесе. Плюс [natrontech/kubelab](https://github.com/natrontech/kubelab).

**Примеры манифестов для копирования и разбора:**
[AdminTurnedDevOps/kubernetes-examples](https://github.com/AdminTurnedDevOps/kubernetes-examples) · [ContainerSolutions/kubernetes-examples](https://github.com/ContainerSolutions/kubernetes-examples) · [nigelpoulton/k8s101](https://github.com/nigelpoulton/k8s101)

**Визуально:** [philippemerle/Awesome-Kubernetes-Architecture-Diagrams](https://github.com/philippemerle/Awesome-Kubernetes-Architecture-Diagrams) — схемы, чтобы уложить архитектуру в голове.

---

### Неделя 3 (25–31 авг): Kubernetes — глубина + Helm

**Понять «как оно работает внутри» — это то, что отличает middle от junior:**
- [jamiehannaford/what-happens-when-k8s](https://github.com/jamiehannaford/what-happens-when-k8s) — **прочитать полностью и уметь рассказать.** Это легендарный вопрос на собесе: «что происходит, когда ты делаешь kubectl run?»
- [kelseyhightower/kubernetes-the-hard-way](https://github.com/kelseyhightower/kubernetes-the-hard-way) — поднять кластер вручную, компонент за компонентом. Это 1–2 дня работы, но после него K8s перестаёт быть магией. **Сильно рекомендую не пропускать.**

**Темы недели:**
- RBAC: ServiceAccount, Role, RoleBinding, ClusterRole — обязательно
- Scheduling: nodeSelector, affinity/anti-affinity, taints/tolerations, topology spread
- Автоскейлинг: HPA, VPA, Cluster Autoscaler → [kedacore/keda](https://github.com/kedacore/keda), [aws/karpenter-provider-aws](https://github.com/aws/karpenter-provider-aws)
- NetworkPolicy → [cilium/cilium](https://github.com/cilium/cilium) (базово, что такое eBPF и зачем)
- Troubleshooting: CrashLoopBackOff, ImagePullBackOff, Pending, Evicted — разобрать причины каждого

**Helm:**
- Написать свой чарт с нуля: values, templates, helpers, зависимости
- [helm/chart-testing](https://github.com/helm/chart-testing) — линт и тесты чартов
- [helmfile/helmfile](https://github.com/helmfile/helmfile) — управление множеством релизов
- [bitnami/readme-generator-for-helm](https://github.com/bitnami/readme-generator-for-helm) — документация к чарту

**Инструменты диагностики (пригодятся и на работе, и как ответ на собесе):**
[eldadru/ksniff](https://github.com/eldadru/ksniff) · [kubeshark/kubeshark](https://github.com/kubeshark/kubeshark) · [kubetail-org/kubetail](https://github.com/kubetail-org/kubetail) · [inspektor-gadget/inspektor-gadget](https://github.com/inspektor-gadget/inspektor-gadget) · [stackrox/kube-linter](https://github.com/stackrox/kube-linter) · [yonahd/kor](https://github.com/yonahd/kor) · [robusta-dev/krr](https://github.com/robusta-dev/krr)

---

### Неделя 4 (1–7 сен): Terraform / IaC 🔴 второй блокер

**Основной источник:**
- [iam-veeramalla/terraform-zero-to-hero](https://github.com/iam-veeramalla/terraform-zero-to-hero) — курс на 7 дней, идеально ложится в неделю
- [brikis98/terraform-up-and-running](https://github.com/brikis98/terraform-up-and-running) — код к книге «Terraform: Up and Running». Это лучший материал по best practices, разобрать примеры модулей.

**Что уметь:**
- providers, resources, data sources, variables, outputs, locals
- **state**: где живёт, зачем remote backend, state locking, `terraform import`, `state mv` — про state спрашивают всегда
- модули: написать свой переиспользуемый модуль
- workspaces vs отдельные каталоги под окружения (и почему второе обычно лучше)
- `plan` в CI, review плана как процесс

**Инструменты:**
- [opentofu/opentofu](https://github.com/opentofu/opentofu) — знать, что это форк и почему появился (частый вопрос «в теме ли ты»)
- [terraform-docs/terraform-docs](https://github.com/terraform-docs/terraform-docs) — автодоки модулей
- [runatlantis/atlantis](https://github.com/runatlantis/atlantis) — Terraform в PR, это уровень «взрослого» процесса
- [idoavrah/terraform-tui](https://github.com/idoavrah/terraform-tui) — навигация по state
- [MatthewJohn/terrareg](https://github.com/MatthewJohn/terrareg) — приватный registry модулей

**Практика без облачного счёта** (важно — не трать деньги):
- [localstack/localstack](https://github.com/localstack/localstack) — эмулятор AWS локально, **основной вариант**
- [ministackorg/ministack](https://github.com/ministackorg/ministack) — альтернатива, 60+ сервисов, совместим с Terraform
- [terraform-yc-modules/terraform-yc-vpc](https://github.com/terraform-yc-modules/terraform-yc-vpc) — если целишься в вакансии с Yandex Cloud (актуально для рынка KZ/CIS)
- [hcloud-k8s/terraform-hcloud-kubernetes](https://github.com/hcloud-k8s/terraform-hcloud-kubernetes) / [vitobotta/hetzner-k3s](https://github.com/vitobotta/hetzner-k3s) — реальный кластер за ~5–10 €/мес, если хочешь настоящее облако дешево

**Справочник:** [shuaibiyy/awesome-tf](https://github.com/shuaibiyy/awesome-tf)

---

### Неделя 5 (8–14 сен): CI/CD в YAML (GitLab CI + GitHub Actions) + Ansible

У тебя уже есть Jenkins — это преимущество, надо просто переложить знание на современный синтаксис.

**GitHub Actions:**
- [nektos/act](https://github.com/nektos/act) — запуск workflow локально, экономит часы
- [cicd-excellence/app](https://github.com/cicd-excellence/app) + [cicd-excellence/infra](https://github.com/cicd-excellence/infra) — **готовый пример полного GitOps CI/CD пайплайна на GH Actions. Разобрать построчно, это шаблон для твоего портфолио.**
- [actions/actions-runner-controller](https://github.com/actions/actions-runner-controller) — self-hosted runners в K8s (сильный пункт в резюме)
- [zizmorcore/zizmor](https://github.com/zizmorcore/zizmor) — статический анализ workflow на безопасность

**GitLab CI:**
- [firecow/gitlab-ci-local](https://github.com/firecow/gitlab-ci-local) — прогон `.gitlab-ci.yml` локально без push
- Освоить: stages, jobs, needs/DAG, rules, artifacts, cache, matrix, шаблоны и `include`, environments

**Ansible:**
- [iam-veeramalla/ansible-zero-to-hero](https://github.com/iam-veeramalla/ansible-zero-to-hero) — основной курс
- [ansible/ansible-examples](https://github.com/ansible/ansible-examples) — официальные примеры плейбуков
- Что уметь: inventory, playbook, roles, handlers, templates (Jinja2), vault, idempotency (**понимать и объяснять — ключевой вопрос**)
- [moltenbit/How-To-Secure-A-Linux-Server-With-Ansible](https://github.com/moltenbit/How-To-Secure-A-Linux-Server-With-Ansible) и [pyllyukko/harden.yml](https://github.com/pyllyukko/harden.yml) — готовые роли по харденингу, отличная практика + пункт «security» в резюме

**Справочники:** [jdauphant/awesome-ansible](https://github.com/jdauphant/awesome-ansible) · [ligurio/awesome-ci](https://github.com/ligurio/awesome-ci) · [myugan/awesome-cicd-security](https://github.com/myugan/awesome-cicd-security)

---

### Неделя 6 (15–21 сен): GitOps + Observability (усилить то, что уже знаешь)

**GitOps — стандарт деплоя, спрашивают после K8s:**
- ArgoCD поставить в свой кластер, задеплоить приложение из Git (App of Apps паттерн)
- [cloudogu/gitops-patterns](https://github.com/cloudogu/gitops-patterns) — паттерны и антипаттерны процесса, читать обязательно
- [akuity/kargo](https://github.com/akuity/kargo) — продвижение релизов между окружениями (dev→stage→prod)
- [zapier/kubechecks](https://github.com/zapier/kubechecks) — проверка изменений до попадания в кластер
- Секреты в GitOps: [isindir/sops-secrets-operator](https://github.com/isindir/sops-secrets-operator), [Infisical/infisical](https://github.com/Infisical/infisical), Vault → [FalcoSuessgott/vault-kubernetes-kms](https://github.com/FalcoSuessgott/vault-kubernetes-kms)

**Observability — здесь ты уже силён, надо перевести на K8s-рельсы:**
- [acend/prometheus-training](https://github.com/acend/prometheus-training) — интерактивный тренинг. **Главное: PromQL.** Уметь писать `rate()`, `irate()`, `histogram_quantile()`, `increase()`, понимать разницу counter/gauge/histogram/summary.
- [samber/awesome-prometheus-alerts](https://github.com/samber/awesome-prometheus-alerts) — готовые правила алертов, растащить в свой проект
- [dotdc/grafana-dashboards-kubernetes](https://github.com/dotdc/grafana-dashboards-kubernetes) — нормальные дашборды для K8s
- [grafana/loki](https://github.com/grafana/loki) — логи; ты знаешь ELK, надо уметь сравнить ELK vs Loki (частый вопрос)
- [prometheus/blackbox_exporter](https://github.com/prometheus/blackbox_exporter) + [ribbybibby/ssl_exporter](https://github.com/ribbybibby/ssl_exporter)
- Трейсинг: OpenTelemetry базово → [SigNoz/signoz](https://github.com/SigNoz/signoz) или [coroot/coroot](https://github.com/coroot/coroot) поставить и посмотреть
- SRE-теория: **[dastergon/awesome-sre](https://github.com/dastergon/awesome-sre)** — обязательно понять SLI/SLO/SLA, error budget, MTTR/MTBF, blameless postmortem. Это спрашивают на всех middle+ собесах, а у тебя есть реальный опыт 24/7 — красиво ложится.
- Алертинг/инциденты: [keephq/keep](https://github.com/keephq/keep), [louislam/uptime-kuma](https://github.com/louislam/uptime-kuma), [TwiN/gatus](https://github.com/TwiN/gatus)

---

### Неделя 7 (22–28 сен): Облако + Security + Networking-добор

**Облако (выбрать одно направление под вакансии, на которые откликаешься):**
- AWS: [mikeroyal/AWS-Guide](https://github.com/mikeroyal/AWS-Guide), [donnemartin/awesome-aws](https://github.com/donnemartin/awesome-aws)
- Минимум, который надо уметь объяснить: VPC/subnet/route table/SG vs NACL, IAM (роли vs пользователи, policy), EC2, S3 (+ политики доступа), RDS, ELB/ALB, EKS, CloudWatch
- Практика бесплатно: [localstack/localstack](https://github.com/localstack/localstack), [sivchari/kumo](https://github.com/sivchari/kumo), [floci-io/floci](https://github.com/floci-io/floci)
- FinOps как бонус-тема: [ravikiranvm/aws-finops-dashboard](https://github.com/ravikiranvm/aws-finops-dashboard), [WozzHQ/wozz](https://github.com/WozzHQ/wozz) — умение говорить про стоимость инфраструктуры сильно выделяет
- Azure, если попадутся вакансии: [lukemurraynz/awesome-azure-architecture](https://github.com/lukemurraynz/awesome-azure-architecture)
- Бесплатные тиры для лаб: [ripienaar/free-for-dev](https://github.com/ripienaar/free-for-dev)

**DevSecOps (у тебя банковский бэкграунд — это твоё естественное преимущество, подчёркивай):**
- [Swordfish-Security/awesome-devsecops-russia](https://github.com/Swordfish-Security/awesome-devsecops-russia) — **на русском, начать с него**
- [aquasecurity/trivy](https://github.com/aquasecurity/trivy) — встроить в пайплайн проекта
- [deepfence/SecretScanner](https://github.com/deepfence/SecretScanner) — поиск секретов
- [kyverno/kyverno](https://github.com/kyverno/kyverno) — policy as code в K8s (Pod Security Standards)
- [madhuakula/kubernetes-goat](https://github.com/madhuakula/kubernetes-goat) — **уязвимый кластер по дизайну. Пройти несколько сценариев — лучший способ понять K8s security и получить готовые истории для собеса.**
- [kubearmor/KubeArmor](https://github.com/kubearmor/KubeArmor), [CISOfy/lynis](https://github.com/CISOfy/lynis), [MegaManSec/Gixy-Next](https://github.com/MegaManSec/Gixy-Next) (аудит nginx-конфигов)
- Supply chain: [vishalgarg-sec/Software-Supply-Chain-Security](https://github.com/vishalgarg-sec/Software-Supply-Chain-Security)
- Доступы: [gravitational/teleport](https://github.com/gravitational/teleport), [keycloak/keycloak](https://github.com/keycloak/keycloak), [goauthentik/authentik](https://github.com/goauthentik/authentik) — хотя бы понимать, зачем они

**Networking — у тебя база сильная, добираем «системный дизайн»:**
- [ByteByteGoHq/system-design-101](https://github.com/ByteByteGoHq/system-design-101) — **прочитать целиком, картинками. Быстро и очень полезно для архитектурных вопросов.**
- [alex/what-happens-when](https://github.com/alex/what-happens-when) — что происходит при вводе google.com. **Классика собеседования, разобрать до конца.**
- [Derssa/Torollo](https://github.com/Derssa/Torollo) — интерактивная песочница по system design и сетям
- [srl-labs/containerlab](https://github.com/srl-labs/containerlab) — лабы по сетям, если хочешь усилить сетевой профиль
- nginx: [fcambus/nginx-resources](https://github.com/fcambus/nginx-resources), [Arlandaren/nginx-template](https://github.com/Arlandaren/nginx-template)
- [netbox-community/netbox](https://github.com/netbox-community/netbox) — source of truth для сетей

---

### Неделя 8 (29 сен — 5 окт): Полировка, повторение, интенсив собеседований

Новых тем НЕ берём. Только:
1. **Мок-экзамены K8s** — [sailor-sh/CK-X](https://github.com/sailor-sh/CK-X): мок CKA/CKAD/CKS с таймером и лабами. Прогнать несколько раз.
2. [dgkanatsios/CKAD-exercises](https://github.com/dgkanatsios/CKAD-exercises) — упражнения на скорость с kubectl
3. Прогон всех вопросов из Трека B ещё раз, вслух, с таймером
4. Доводка 4 проектов портфолио + README к каждому
5. Активные отклики и собеседования каждый день

---

## 4. ТРЕК B — подготовка к собеседованиям (каждый день с первого дня)

### Главный ресурс
**[bregman-arie/devops-exercises](https://github.com/bregman-arie/devops-exercises)** — это твой основной тренажёр вопросов. Огромная база по всем темам с ответами.
Метод: **20 вопросов в день, отвечать ВСЛУХ, потом сверять.** Не читать глазами — на собесе ты говоришь, а не читаешь. Отмечать те, где поплыл, возвращаться через 3 дня.

### Остальные банки вопросов (из твоих звёзд)
| Репозиторий | Что даёт |
|---|---|
| [moabukar/tech-vault](https://github.com/moabukar/tech-vault) | Вопросы + реальные практические задачи-челленджи |
| [Swfuse/devops-interview](https://github.com/Swfuse/devops-interview) | Вопросы по DevOps и системному администрированию |
| [rmntrvn/adm_linux_ops_questions](https://github.com/rmntrvn/adm_linux_ops_questions) | **На русском** — вопросы для Linux-админов и DevOps. Очень близко к тому, что спрашивают на рынке РФ/КЗ |
| [trimstray/test-your-sysadmin-skills](https://github.com/trimstray/test-your-sysadmin-skills) | 284 вопроса по Linux с ответами — проверка глубины |
| [bregman-arie/devops-resources](https://github.com/bregman-arie/devops-resources) | Дополнение к devops-exercises |
| [NotHarshhaa/into-the-devops](https://github.com/NotHarshhaa/into-the-devops) | Разбор по темам: Linux, Jenkins, AWS, SRE, Prometheus, Docker, Ansible, K8s, Terraform |

### Шпаргалки — прогонять за 15 минут перед каждым собеседованием
[NotHarshhaa/devops-cheatsheet](https://github.com/NotHarshhaa/devops-cheatsheet) · [LeCoupa/awesome-cheatsheets](https://github.com/LeCoupa/awesome-cheatsheets) · [arslanbilal/git-cheat-sheet](https://github.com/arslanbilal/git-cheat-sheet) · [devaaravmishra/git-commands](https://github.com/devaaravmishra/git-commands) · [crescentpartha/CheatSheets-for-Developers](https://github.com/crescentpartha/CheatSheets-for-Developers)

### Вопросы, которые спросят почти наверняка — подготовь ответы письменно
**Linux**
- Что происходит при загрузке Linux от BIOS до shell?
- SIGTERM vs SIGKILL. Что делает `kill -9` и почему это плохо?
- `df` показывает 100%, `du` — 50%. Почему? (удалённый файл с открытым дескриптором)
- Что такое load average 1/5/15, и когда 10 — это норма?
- Как найти, что съело диск / память / CPU? Пошагово.
- Hard link vs symlink. Что в inode?
- Как посмотреть, какой процесс слушает порт?

**Docker**
- Контейнер vs VM. Что такое namespaces и cgroups?
- COPY vs ADD, CMD vs ENTRYPOINT
- Как уменьшить образ? (multi-stage, distroless, слои, .dockerignore)
- Куда деваются данные при удалении контейнера? Виды volume.
- Docker network: bridge, host, none, overlay
- Почему нельзя запускать процесс от root в контейнере?

**Kubernetes**
- Опиши архитектуру кластера. За что отвечает каждый компонент?
- Что происходит по шагам при `kubectl apply -f deployment.yaml`?
- Pod в CrashLoopBackOff — твои действия по шагам?
- Pod в Pending — причины? (ресурсы, taints, PVC, affinity)
- Liveness vs readiness vs startup probe. Что будет, если перепутать?
- requests vs limits. Что такое QoS-классы? Кого убьют первым при нехватке памяти?
- Как обновить приложение без простоя? Rolling update, maxSurge/maxUnavailable
- Service ClusterIP → как трафик доходит до Pod?
- Deployment vs StatefulSet. Когда нужен StatefulSet?
- Как хранить секреты правильно? (Secret в etcd — base64, не шифрование!)

**CI/CD и Git**
- merge vs rebase, когда что. Что такое `git rebase -i`?
- Как откатить закоммиченное? `revert` vs `reset --hard` vs `reset --soft`
- Что такое cherry-pick и когда он спасает?
- Опиши свой идеальный пайплайн от коммита до прода
- Как хранить секреты в CI? Как НЕ надо?
- Blue-green vs canary vs rolling. Что выберешь и почему?
- Как откатить неудачный релиз в проде?

**Terraform**
- Зачем нужен state и что будет, если его потерять?
- Как работать со state в команде? (remote backend + locking)
- `terraform import` — зачем?
- Как не хранить пароли в .tf?
- Что делать, если кто-то поменял ресурс руками в консоли?

**Мониторинг / SRE**
- Pull vs push модель метрик. Почему Prometheus — pull?
- Counter vs gauge vs histogram
- Что такое SLI/SLO/SLA и error budget?
- Как строишь алертинг, чтобы не было alert fatigue?
- Сервис лежит. Твои действия в первые 5 минут?

**Про опыт (готовь истории по STAR — у тебя есть материал из Kaspi)**
- Расскажи про самый серьёзный инцидент, который разбирал
- Что ты автоматизировал и сколько времени это сэкономило?
- Расскажи про случай, когда сломал прод. Как чинил, какие выводы?
- Почему уходишь / ищешь новое место?

---

## 5. ТРЕК C — портфолио: 4 проекта (по одному в 2 недели)

Пустой GitHub = отказ. Твой профиль сейчас содержит только README с резюме. Нужны живые репозитории. **Каждый проект = отдельный публичный репо с подробным README, схемой архитектуры и скриншотами.**

### Проект 1 (недели 1–2): `docker-production-app`
Контейнеризация приложения по-взрослому.
- Multi-stage Dockerfile, non-root user, distroless или alpine
- docker-compose с приложением + Postgres + nginx
- Прогон hadolint и trivy, результаты в README («образ 1.2 GB → 80 MB, 14 CVE → 0»)
- Мониторинг из [stefanprodan/dockprom](https://github.com/stefanprodan/dockprom) — Prometheus + Grafana + cAdvisor + node-exporter
- **README должен содержать**: зачем, схема, как запустить, что улучшено и на сколько

### Проект 2 (недели 3–4): `k8s-platform`
Приложение в Kubernetes как надо.
- Свой Helm-чарт: deployment, service, ingress, configmap, secret, HPA, PDB
- Probes настроены осознанно, requests/limits выставлены
- NetworkPolicy, RBAC с минимальными правами, ServiceAccount
- kube-linter и trivy в проверках
- Мониторинг: Prometheus + дашборды из [dotdc/grafana-dashboards-kubernetes](https://github.com/dotdc/grafana-dashboards-kubernetes) + алерты из [samber/awesome-prometheus-alerts](https://github.com/samber/awesome-prometheus-alerts)
- В README — раздел «Troubleshooting»: какие проблемы ловил и как решил. Это читают внимательнее всего.

### Проект 3 (недели 5–6): `infra-as-code`
IaC + пайплайн.
- Terraform: модули (network, compute, k8s), remote state, окружения dev/prod
- Ansible: роли для базовой настройки и харденинга серверов
- CI: GitHub Actions с `fmt` → `validate` → `tflint` → `plan` на PR → `apply` на merge
- [terraform-docs](https://github.com/terraform-docs/terraform-docs) для автодокументации модулей
- Работает на LocalStack или на Hetzner (дешёвое реальное облако)

### Проект 4 (недели 7–8): `gitops-pipeline` — флагманский
Полный путь от коммита до прода. Это проект, который ты показываешь на собеседовании первым.
- Репо приложения + репо инфраструктуры (по образцу [cicd-excellence/app](https://github.com/cicd-excellence/app) и [cicd-excellence/infra](https://github.com/cicd-excellence/infra))
- CI: тесты → сборка образа → trivy scan → push в registry → bump тега в infra-репо
- CD: ArgoCD подхватывает и синхронизирует
- Секреты через SOPS или Infisical
- Kyverno-политики, мониторинг и алерты
- Схема архитектуры в README (можно нарисовать в [ShadowArcanist/netviz](https://github.com/ShadowArcanist/netviz) или mermaid)
- Демонстрация rollback: сломать релиз и откатить, приложить лог

**Идеи для дополнительных проектов, если останется время:** [NotHarshhaa/DevOps-Projects](https://github.com/NotHarshhaa/DevOps-Projects) — реальные проекты по AWS/K8s/Docker.

---

## 6. Сертификаты — стоит ли

**Коротко: одна сертификация имеет смысл — CKA.** Она реально закрывает вопрос «а он умеет Kubernetes?» в глазах HR и фильтров вакансий.

- **CKA (Certified Kubernetes Administrator)** — целиться на конец октября, после недели 8. Экзамен практический, а не тестовый, поэтому подготовка = реальный навык, не зря потраченное время.
- Программа: [cncf/curriculum](https://github.com/cncf/curriculum) — официальный учебный план
- Подготовка: [sailor-sh/CK-X](https://github.com/sailor-sh/CK-X) (мок-экзамены с таймером), [dgkanatsios/CKAD-exercises](https://github.com/dgkanatsios/CKAD-exercises) (упражнения на скорость)
- **Купоны и скидки:** [techiescamp/linux-foundation-coupon](https://github.com/techiescamp/linux-foundation-coupon) — экзамен часто можно взять на 40–50% дешевле. Не покупай по полной цене.
- Бесплатные бейджи для профиля: [CloudNativeStudyGroup/Free-Credly-Badges](https://github.com/CloudNativeStudyGroup/Free-Credly-Badges)
- CKS — позже, когда будет работа. У тебя банковский профиль, security-специализация — хороший долгосрочный вектор. Мок: [thiago4he/kubernetes-security-kcsa-mock](https://github.com/thiago4he/kubernetes-security-kcsa-mock), практика: [madhuakula/kubernetes-goat](https://github.com/madhuakula/kubernetes-goat), [ViktorUJ/cks](https://github.com/ViktorUJ/cks)

Terraform Associate — необязательно, дешевле показать проект. AWS SAA — только если целишься именно в AWS-вакансии.

---

## 7. Ежедневная рутина

**Рабочий день (2 часа):**
```
20 мин  Трек B: 20 вопросов из devops-exercises вслух
80 мин  Трек A: тема недели, руками в кластере
20 мин  Записать в конспект: что сделал, что не понял
```

**Выходной (4 часа):**
```
3 ч   Трек C: проект недели
1 ч   Повторение вопросов, где плыл (интервальное повторение)
```

**Каждую пятницу — 30 минут ретро:**
- Что из плана недели не закрыл? Переносим или выкидываем?
- Сколько откликов отправил? Сколько собеседований было?
- Что спросили на собесах, чего я не знал? → это добавляется в план приоритетно

**Отклики:** 5–10 вакансий в неделю, начиная с недели 0. Не ждать «готовности» — каждое собеседование даёт точный список того, что учить.

---

## 8. Правила, без которых план не сработает

1. **Не открывай остальные 480 звёзд до оффера.** Self-hosted-приложения, файловые менеджеры, PDF-инструменты, iOS-твики — это развлечение, не учёба. Главный риск твоего плана не «мало материала», а **распыление**.
2. **Один источник на тему.** Если начал Fast-Kubernetes — не переключайся на другой курс на третий день.
3. **Руками, а не глазами.** Просмотренный туториал ≠ навык. Каждая тема заканчивается тем, что ты что-то сломал и починил в своём кластере.
4. **Собеседования параллельно, а не после.** Это часть обучения, самая эффективная его часть.
5. **Kubernetes и Terraform — это 70% результата.** Если на что-то не хватает времени, режь мониторинг и облако, но не эти две темы.
6. **Продавай то, что у тебя уже есть.** 9 лет инфраструктуры, банк, продакшн, 24/7, реальные инциденты, Jenkins в бою — у большинства кандидатов, знающих K8s по курсам, этого нет. Твоя позиция на собеседовании: «я умею держать прод, а K8s и Terraform — вот мои проекты».

---

## 9. Контрольные точки

| Дата | Что должно быть сделано |
|---|---|
| 17 авг | Кластер работает, Docker на продакшн-уровне, Проект 1 готов, 100+ вопросов пройдено |
| 31 авг | K8s: уверенно объясняю архитектуру и troubleshooting, Helm-чарт свой, Проект 2 готов |
| 14 сен | Terraform + Ansible + CI/CD в YAML, Проект 3 готов |
| 28 сен | GitOps + мониторинг в K8s, Проект 4 готов, 400+ вопросов пройдено |
| 5 окт | Все проекты отполированы, мок-экзамены CKA сданы, идут финальные этапы собеседований |

---

## 10. Полная карта твоих starred-репозиториев по категориям

Чтобы больше не искать — вот всё релевантное из 546 звёзд, сгруппированное. Используй как справочник, но помни правило №1.

<details>
<summary><b>Дорожные карты и общие курсы</b></summary>

[milanm/DevOps-Roadmap](https://github.com/milanm/DevOps-Roadmap) · [nilbuild/developer-roadmap](https://github.com/nilbuild/developer-roadmap) · [bregman-arie/devops-exercises](https://github.com/bregman-arie/devops-exercises) · [bregman-arie/devops-resources](https://github.com/bregman-arie/devops-resources) · [codeaprendiz/learn-devops](https://github.com/codeaprendiz/learn-devops) · [Tikam02/DevOps-Guide](https://github.com/Tikam02/DevOps-Guide) · [NotHarshhaa/into-the-devops](https://github.com/NotHarshhaa/into-the-devops) · [devops-by-examples/complete-devops-course](https://github.com/devops-by-examples/complete-devops-course) · [manikcloud/DevOps-Tutorial](https://github.com/manikcloud/DevOps-Tutorial) · [Lets-DevOps/awesome-learning](https://github.com/Lets-DevOps/awesome-learning) · [wmariuss/awesome-devops](https://github.com/wmariuss/awesome-devops) · [awesome-soft/awesome-devops](https://github.com/awesome-soft/awesome-devops) · [UttkarshKesharwani/Kodekloud-100DaysOfDevops](https://github.com/UttkarshKesharwani/Kodekloud-100DaysOfDevops) · [joseadanof/awesome-cloudnative-trainings](https://github.com/joseadanof/awesome-cloudnative-trainings) · [rootsongjc/awesome-cloud-native](https://github.com/rootsongjc/awesome-cloud-native) · [practical-tutorials/project-based-learning](https://github.com/practical-tutorials/project-based-learning) · [codecrafters-io/build-your-own-x](https://github.com/codecrafters-io/build-your-own-x)
</details>

<details>
<summary><b>Linux, shell, sysadmin</b></summary>

[Sagar2366/linux_the_final_boss](https://github.com/Sagar2366/linux_the_final_boss) · [mikeroyal/Linux-Guide](https://github.com/mikeroyal/Linux-Guide) · [iximiuz/shellgym](https://github.com/iximiuz/shellgym) · [kilian-ai/linuxontab](https://github.com/kilian-ai/linuxontab) · [trimstray/test-your-sysadmin-skills](https://github.com/trimstray/test-your-sysadmin-skills) · [rmntrvn/adm_linux_ops_questions](https://github.com/rmntrvn/adm_linux_ops_questions) · [krekhovx/krxnotes](https://github.com/krekhovx/krxnotes) · [proninyaroslav/linux-insides-ru](https://github.com/proninyaroslav/linux-insides-ru) · [makelinux/linux_kernel_map](https://github.com/makelinux/linux_kernel_map) · [imthenachoman/How-To-Secure-A-Linux-Server](https://github.com/imthenachoman/How-To-Secure-A-Linux-Server) · [trimstray/the-practical-linux-hardening-guide](https://github.com/trimstray/the-practical-linux-hardening-guide) · [trimstray/the-book-of-secret-knowledge](https://github.com/trimstray/the-book-of-secret-knowledge) · [chubin/cheat.sh](https://github.com/chubin/cheat.sh) · [koalaman/shellcheck](https://github.com/koalaman/shellcheck) · [mvdan/sh](https://github.com/mvdan/sh) · [HariSekhon/DevOps-Bash-tools](https://github.com/HariSekhon/DevOps-Bash-tools) · [strace/strace](https://github.com/strace/strace) · [muesli/duf](https://github.com/muesli/duf) · [atuinsh/atuin](https://github.com/atuinsh/atuin) · [kahun/awesome-sysadmin](https://github.com/kahun/awesome-sysadmin) · [awesome-foss/awesome-sysadmin](https://github.com/awesome-foss/awesome-sysadmin) · [moul/awesome-ssh](https://github.com/moul/awesome-ssh) · [PatchMon/PatchMon](https://github.com/PatchMon/PatchMon)
</details>

<details>
<summary><b>Docker и контейнеры</b></summary>

[iam-veeramalla/Docker-Zero-to-Hero](https://github.com/iam-veeramalla/Docker-Zero-to-Hero) · [dnaprawa/dockerfile-best-practices](https://github.com/dnaprawa/dockerfile-best-practices) · [hadolint/hadolint](https://github.com/hadolint/hadolint) · [deckrun/dockadvisor](https://github.com/deckrun/dockadvisor) · [wagoodman/dive](https://github.com/wagoodman/dive) · [docker/docker-bench-security](https://github.com/docker/docker-bench-security) · [myugan/awesome-docker-security](https://github.com/myugan/awesome-docker-security) · [veggiemonk/awesome-docker](https://github.com/veggiemonk/awesome-docker) · [jesseduffield/lazydocker](https://github.com/jesseduffield/lazydocker) · [bcicen/ctop](https://github.com/bcicen/ctop) · [lirantal/dockly](https://github.com/lirantal/dockly) · [nicolaka/netshoot](https://github.com/nicolaka/netshoot) · [hoalongnatsu/Dockerfile](https://github.com/hoalongnatsu/Dockerfile) · [LaggerIsME/docker-cleanup](https://github.com/LaggerIsME/docker-cleanup) · [stefanprodan/dockprom](https://github.com/stefanprodan/dockprom) · [rootless-containers/rootlesskit](https://github.com/rootless-containers/rootlesskit) · [Gosayram/kaniko](https://github.com/Gosayram/kaniko) · [project-stacker/stacker](https://github.com/project-stacker/stacker) · [apple/container](https://github.com/apple/container)
</details>

<details>
<summary><b>Kubernetes — обучение</b></summary>

[kelseyhightower/kubernetes-the-hard-way](https://github.com/kelseyhightower/kubernetes-the-hard-way) · [omerbsezer/Fast-Kubernetes](https://github.com/omerbsezer/Fast-Kubernetes) · [iam-veeramalla/Kubernetes-Zero-to-Hero](https://github.com/iam-veeramalla/Kubernetes-Zero-to-Hero) · [techiescamp/kubernetes-learning-path](https://github.com/techiescamp/kubernetes-learning-path) · [nigelpoulton/k8s101](https://github.com/nigelpoulton/k8s101) · [Manoj-engineer/k8squest](https://github.com/Manoj-engineer/k8squest) · [natrontech/kubelab](https://github.com/natrontech/kubelab) · [jamiehannaford/what-happens-when-k8s](https://github.com/jamiehannaford/what-happens-when-k8s) · [AdminTurnedDevOps/kubernetes-examples](https://github.com/AdminTurnedDevOps/kubernetes-examples) · [ContainerSolutions/kubernetes-examples](https://github.com/ContainerSolutions/kubernetes-examples) · [philippemerle/Awesome-Kubernetes-Architecture-Diagrams](https://github.com/philippemerle/Awesome-Kubernetes-Architecture-Diagrams) · [ramitsurana/awesome-kubernetes](https://github.com/ramitsurana/awesome-kubernetes) · [collabnix/kubetools](https://github.com/collabnix/kubetools) · [vilaca/awesome-k8s-tools](https://github.com/vilaca/awesome-k8s-tools) · [iximiuz/kexp](https://github.com/iximiuz/kexp) · [ngrok/webernetes](https://github.com/ngrok/webernetes) · [kubernetes/kubernetes](https://github.com/kubernetes/kubernetes) · [kubernetes-sigs/kube-scheduler-simulator](https://github.com/kubernetes-sigs/kube-scheduler-simulator)
</details>

<details>
<summary><b>Kubernetes — сертификация</b></summary>

[cncf/curriculum](https://github.com/cncf/curriculum) · [sailor-sh/CK-X](https://github.com/sailor-sh/CK-X) · [dgkanatsios/CKAD-exercises](https://github.com/dgkanatsios/CKAD-exercises) · [ViktorUJ/cks](https://github.com/ViktorUJ/cks) · [thiago4he/kubernetes-security-kcsa-mock](https://github.com/thiago4he/kubernetes-security-kcsa-mock) · [madhuakula/kubernetes-goat](https://github.com/madhuakula/kubernetes-goat) · [techiescamp/linux-foundation-coupon](https://github.com/techiescamp/linux-foundation-coupon) · [CloudNativeStudyGroup/Free-Credly-Badges](https://github.com/CloudNativeStudyGroup/Free-Credly-Badges)
</details>

<details>
<summary><b>Kubernetes — дистрибутивы и развёртывание</b></summary>

[k3s-io/k3s](https://github.com/k3s-io/k3s) · [k3d-io/k3d](https://github.com/k3d-io/k3d) · [k0sproject/k0s](https://github.com/k0sproject/k0s) · [rancher/k3k](https://github.com/rancher/k3k) · [vitobotta/hetzner-k3s](https://github.com/vitobotta/hetzner-k3s) · [hcloud-k8s/terraform-hcloud-kubernetes](https://github.com/hcloud-k8s/terraform-hcloud-kubernetes) · [kubermatic/kubeone](https://github.com/kubermatic/kubeone) · [kubean-io/kubean](https://github.com/kubean-io/kubean) · [replicatedhq/kURL](https://github.com/replicatedhq/kURL) · [cozystack/cozystack](https://github.com/cozystack/cozystack) · [kubero-dev/kubero](https://github.com/kubero-dev/kubero) · [rootless-containers/usernetes](https://github.com/rootless-containers/usernetes)
</details>

<details>
<summary><b>Kubernetes — ежедневный тулинг и UI</b></summary>

[derailed/k9s](https://github.com/derailed/k9s) · [ahmetb/kubectx](https://github.com/ahmetb/kubectx) · [danielfoehrKn/kubeswitch](https://github.com/danielfoehrKn/kubeswitch) · [kubewall/kubewall](https://github.com/kubewall/kubewall) · [freelensapp/freelens](https://github.com/freelensapp/freelens) · [aptakube/aptakube](https://github.com/aptakube/aptakube) · [kite-org/kite](https://github.com/kite-org/kite) · [skyhook-io/radar](https://github.com/skyhook-io/radar) · [openobserve/kide](https://github.com/openobserve/kide) · [gerbil/kubegui](https://github.com/gerbil/kubegui) · [kbterm/kubeterm](https://github.com/kbterm/kubeterm) · [swade1987/kubernetes-toolkit](https://github.com/swade1987/kubernetes-toolkit) · [kubetail-org/kubetail](https://github.com/kubetail-org/kubetail) · [eldadru/ksniff](https://github.com/eldadru/ksniff) · [kubeshark/kubeshark](https://github.com/kubeshark/kubeshark) · [gma1k/podtrace](https://github.com/gma1k/podtrace) · [inspektor-gadget/inspektor-gadget](https://github.com/inspektor-gadget/inspektor-gadget) · [AvitalTamir/cyphernetes](https://github.com/AvitalTamir/cyphernetes) · [yashbhutwala/kubectl-df-pv](https://github.com/yashbhutwala/kubectl-df-pv) · [AKSarav/KubeNodeUsage](https://github.com/AKSarav/KubeNodeUsage)
</details>

<details>
<summary><b>Kubernetes — качество, политики, оптимизация</b></summary>

[stackrox/kube-linter](https://github.com/stackrox/kube-linter) · [zapier/kubechecks](https://github.com/zapier/kubechecks) · [yonahd/kor](https://github.com/yonahd/kor) · [gianlucam76/k8s-cleaner](https://github.com/gianlucam76/k8s-cleaner) · [robusta-dev/krr](https://github.com/robusta-dev/krr) · [kruize/autotune](https://github.com/kruize/autotune) · [unagex/kondense](https://github.com/unagex/kondense) · [kyverno/kyverno](https://github.com/kyverno/kyverno) · [kedacore/keda](https://github.com/kedacore/keda) · [aws/karpenter-provider-aws](https://github.com/aws/karpenter-provider-aws) · [kubernetes-sigs/kueue](https://github.com/kubernetes-sigs/kueue) · [ctrox/zeropod](https://github.com/ctrox/zeropod) · [rekuberate-io/sleepcycles](https://github.com/rekuberate-io/sleepcycles) · [WozzHQ/wozz](https://github.com/WozzHQ/wozz) · [acrlabs/simkube](https://github.com/acrlabs/simkube) · [wave-k8s/wave](https://github.com/wave-k8s/wave) · [kubernetes-sigs/kro](https://github.com/kubernetes-sigs/kro)
</details>

<details>
<summary><b>Helm и управление манифестами</b></summary>

[helm/chart-testing](https://github.com/helm/chart-testing) · [helmfile/helmfile](https://github.com/helmfile/helmfile) · [bitnami/readme-generator-for-helm](https://github.com/bitnami/readme-generator-for-helm) · [werf/nelm](https://github.com/werf/nelm) · [grafana/tanka](https://github.com/grafana/tanka) · [kluctl/kluctl](https://github.com/kluctl/kluctl) · [cyclops-ui/cyclops](https://github.com/cyclops-ui/cyclops) · [score-spec/spec](https://github.com/score-spec/spec) · [radius-project/radius](https://github.com/radius-project/radius)
</details>

<details>
<summary><b>CI/CD и GitOps</b></summary>

[cicd-excellence/app](https://github.com/cicd-excellence/app) · [cicd-excellence/infra](https://github.com/cicd-excellence/infra) · [nektos/act](https://github.com/nektos/act) · [firecow/gitlab-ci-local](https://github.com/firecow/gitlab-ci-local) · [actions/actions-runner-controller](https://github.com/actions/actions-runner-controller) · [zizmorcore/zizmor](https://github.com/zizmorcore/zizmor) · [cloudogu/gitops-patterns](https://github.com/cloudogu/gitops-patterns) · [akuity/kargo](https://github.com/akuity/kargo) · [pipe-cd/pipecd](https://github.com/pipe-cd/pipecd) · [harness/harness](https://github.com/harness/harness) · [runatlantis/atlantis](https://github.com/runatlantis/atlantis) · [stevius10/Proxmox-GitOps](https://github.com/stevius10/Proxmox-GitOps) · [trublast/vault-plugin-gitops](https://github.com/trublast/vault-plugin-gitops) · [backstage/backstage](https://github.com/backstage/backstage) · [temporalio/temporal](https://github.com/temporalio/temporal) · [argoproj-labs/hera](https://github.com/argoproj-labs/hera) · [ligurio/awesome-ci](https://github.com/ligurio/awesome-ci) · [myugan/awesome-cicd-security](https://github.com/myugan/awesome-cicd-security) · [dokku/dokku](https://github.com/dokku/dokku) · [shuttle-hq/shuttle](https://github.com/shuttle-hq/shuttle)
</details>

<details>
<summary><b>Terraform / IaC</b></summary>

[iam-veeramalla/terraform-zero-to-hero](https://github.com/iam-veeramalla/terraform-zero-to-hero) · [brikis98/terraform-up-and-running](https://github.com/brikis98/terraform-up-and-running) · [shuaibiyy/awesome-tf](https://github.com/shuaibiyy/awesome-tf) · [opentofu/opentofu](https://github.com/opentofu/opentofu) · [terraform-docs/terraform-docs](https://github.com/terraform-docs/terraform-docs) · [idoavrah/terraform-tui](https://github.com/idoavrah/terraform-tui) · [MatthewJohn/terrareg](https://github.com/MatthewJohn/terrareg) · [stategraph/stategraph](https://github.com/stategraph/stategraph) · [terraform-yc-modules/terraform-yc-vpc](https://github.com/terraform-yc-modules/terraform-yc-vpc) · [NordCoderd/cloud-security-plugin](https://github.com/NordCoderd/cloud-security-plugin) · [itsumma/kulebiac](https://github.com/itsumma/kulebiac) · [uatec/teleform](https://github.com/uatec/teleform)
</details>

<details>
<summary><b>Ansible</b></summary>

[iam-veeramalla/ansible-zero-to-hero](https://github.com/iam-veeramalla/ansible-zero-to-hero) · [ansible/ansible-examples](https://github.com/ansible/ansible-examples) · [jdauphant/awesome-ansible](https://github.com/jdauphant/awesome-ansible) · [ansible-community/awesome-ansible](https://github.com/ansible-community/awesome-ansible) · [moltenbit/How-To-Secure-A-Linux-Server-With-Ansible](https://github.com/moltenbit/How-To-Secure-A-Linux-Server-With-Ansible) · [pyllyukko/harden.yml](https://github.com/pyllyukko/harden.yml)
</details>

<details>
<summary><b>Облака</b></summary>

[mikeroyal/AWS-Guide](https://github.com/mikeroyal/AWS-Guide) · [donnemartin/awesome-aws](https://github.com/donnemartin/awesome-aws) · [localstack/localstack](https://github.com/localstack/localstack) · [ministackorg/ministack](https://github.com/ministackorg/ministack) · [floci-io/floci](https://github.com/floci-io/floci) · [sivchari/kumo](https://github.com/sivchari/kumo) · [ravikiranvm/aws-finops-dashboard](https://github.com/ravikiranvm/aws-finops-dashboard) · [maruina/aws-auth-manager](https://github.com/maruina/aws-auth-manager) · [lukemurraynz/awesome-azure-architecture](https://github.com/lukemurraynz/awesome-azure-architecture) · [ripienaar/free-for-dev](https://github.com/ripienaar/free-for-dev) · [openshift/hypershift](https://github.com/openshift/hypershift)
</details>

<details>
<summary><b>Мониторинг, логи, SRE</b></summary>

[acend/prometheus-training](https://github.com/acend/prometheus-training) · [warpnet/awesome-prometheus](https://github.com/warpnet/awesome-prometheus) · [samber/awesome-prometheus-alerts](https://github.com/samber/awesome-prometheus-alerts) · [prometheus/blackbox_exporter](https://github.com/prometheus/blackbox_exporter) · [ribbybibby/ssl_exporter](https://github.com/ribbybibby/ssl_exporter) · [grafana/loki](https://github.com/grafana/loki) · [dotdc/grafana-dashboards-kubernetes](https://github.com/dotdc/grafana-dashboards-kubernetes) · [grafana/beyla](https://github.com/grafana/beyla) · [SigNoz/signoz](https://github.com/SigNoz/signoz) · [openobserve/openobserve](https://github.com/openobserve/openobserve) · [coroot/coroot](https://github.com/coroot/coroot) · [hyperdxio/hyperdx](https://github.com/hyperdxio/hyperdx) · [netdata/netdata](https://github.com/netdata/netdata) · [openlit/openlit](https://github.com/openlit/openlit) · [Enapiuz/awesome-monitoring](https://github.com/Enapiuz/awesome-monitoring) · [louislam/uptime-kuma](https://github.com/louislam/uptime-kuma) · [TwiN/gatus](https://github.com/TwiN/gatus) · [henrygd/beszel](https://github.com/henrygd/beszel) · [keephq/keep](https://github.com/keephq/keep) · [grafana-cold-storage/oncall](https://github.com/grafana-cold-storage/oncall) · [getpusk/pusk](https://github.com/getpusk/pusk) · [slok/alertgram](https://github.com/slok/alertgram) · [sensu/sensu-go](https://github.com/sensu/sensu-go) · [stolostron/multicluster-observability-operator](https://github.com/stolostron/multicluster-observability-operator) · [dastergon/awesome-sre](https://github.com/dastergon/awesome-sre) · [HolmesGPT/holmesgpt](https://github.com/HolmesGPT/holmesgpt) · [k8sgpt-ai/k8sgpt](https://github.com/k8sgpt-ai/k8sgpt)
</details>

<details>
<summary><b>Безопасность и DevSecOps</b></summary>

[Swordfish-Security/awesome-devsecops-russia](https://github.com/Swordfish-Security/awesome-devsecops-russia) · [devsecops/awesome-devsecops](https://github.com/devsecops/awesome-devsecops) · [sottlmarek/DevSecOps](https://github.com/sottlmarek/DevSecOps) · [aquasecurity/trivy](https://github.com/aquasecurity/trivy) · [deepfence/SecretScanner](https://github.com/deepfence/SecretScanner) · [CISOfy/lynis](https://github.com/CISOfy/lynis) · [MegaManSec/Gixy-Next](https://github.com/MegaManSec/Gixy-Next) · [kubearmor/KubeArmor](https://github.com/kubearmor/KubeArmor) · [vishalgarg-sec/Software-Supply-Chain-Security](https://github.com/vishalgarg-sec/Software-Supply-Chain-Security) · [Infisical/infisical](https://github.com/Infisical/infisical) · [FalcoSuessgott/vault-kubernetes-kms](https://github.com/FalcoSuessgott/vault-kubernetes-kms) · [isindir/sops-secrets-operator](https://github.com/isindir/sops-secrets-operator) · [0xn3va/cheat-sheets](https://github.com/0xn3va/cheat-sheets) · [gravitational/teleport](https://github.com/gravitational/teleport) · [keycloak/keycloak](https://github.com/keycloak/keycloak) · [goauthentik/authentik](https://github.com/goauthentik/authentik) · [zitadel/zitadel](https://github.com/zitadel/zitadel) · [pomerium/pomerium](https://github.com/pomerium/pomerium) · [warp-tech/warpgate](https://github.com/warp-tech/warpgate) · [vmware/pinniped](https://github.com/vmware/pinniped) · [Jet-Security-Team/img-authz-plugin](https://github.com/Jet-Security-Team/img-authz-plugin)
</details>

<details>
<summary><b>Сети и system design</b></summary>

[ByteByteGoHq/system-design-101](https://github.com/ByteByteGoHq/system-design-101) · [alex/what-happens-when](https://github.com/alex/what-happens-when) · [Derssa/Torollo](https://github.com/Derssa/Torollo) · [srl-labs/containerlab](https://github.com/srl-labs/containerlab) · [ShadowArcanist/netviz](https://github.com/ShadowArcanist/netviz) · [karam-ajaj/atlas](https://github.com/karam-ajaj/atlas) · [netbox-community/netbox](https://github.com/netbox-community/netbox) · [cilium/cilium](https://github.com/cilium/cilium) · [microsoft/retina](https://github.com/microsoft/retina) · [nginx/nginx-gateway-fabric](https://github.com/nginx/nginx-gateway-fabric) · [kgateway-dev/kgateway](https://github.com/kgateway-dev/kgateway) · [howardjohn/gateway-api-bench](https://github.com/howardjohn/gateway-api-bench) · [ubermorgenland/ingress-migration-kit](https://github.com/ubermorgenland/ingress-migration-kit) · [fcambus/nginx-resources](https://github.com/fcambus/nginx-resources) · [Arlandaren/nginx-template](https://github.com/Arlandaren/nginx-template) · [the-tcpdump-group/tcpdump](https://github.com/the-tcpdump-group/tcpdump) · [gcla/termshark](https://github.com/gcla/termshark) · [GyulyVGC/sniffnet](https://github.com/GyulyVGC/sniffnet) · [arkime/arkime](https://github.com/arkime/arkime) · [kffl/speedbump](https://github.com/kffl/speedbump) · [tsenart/vegeta](https://github.com/tsenart/vegeta)
</details>

<details>
<summary><b>Базы данных и очереди</b></summary>

[pg-tr/awesome-postgres](https://github.com/pg-tr/awesome-postgres) · [dhamaniasad/awesome-postgres](https://github.com/dhamaniasad/awesome-postgres) · [pgbouncer/pgbouncer](https://github.com/pgbouncer/pgbouncer) · [darold/pgbadger](https://github.com/darold/pgbadger) · [cloudnative-pg/cloudnative-pg](https://github.com/cloudnative-pg/cloudnative-pg) · [flyway/flyway](https://github.com/flyway/flyway) · [eduardolat/pgbackweb](https://github.com/eduardolat/pgbackweb) · [databasus/databasus](https://github.com/databasus/databasus) · [databacker/mysql-backup](https://github.com/databacker/mysql-backup) · [gobackup/gobackup](https://github.com/gobackup/gobackup) · [veegres/ivory](https://github.com/veegres/ivory) · [GreenmaskIO/greenmask](https://github.com/GreenmaskIO/greenmask) · [apache/kafka](https://github.com/apache/kafka) · [kafbat/kafka-ui](https://github.com/kafbat/kafka-ui) · [sauljabin/kaskade](https://github.com/sauljabin/kaskade) · [openebs/openebs](https://github.com/openebs/openebs) · [backube/volsync](https://github.com/backube/volsync)
</details>

<details>
<summary><b>Git и рабочие инструменты</b></summary>

[jesseduffield/lazygit](https://github.com/jesseduffield/lazygit) · [dlvhdr/gh-dash](https://github.com/dlvhdr/gh-dash) · [arslanbilal/git-cheat-sheet](https://github.com/arslanbilal/git-cheat-sheet) · [devaaravmishra/git-commands](https://github.com/devaaravmishra/git-commands) · [charmbracelet/soft-serve](https://github.com/charmbracelet/soft-serve) · [ghostty-org/ghostty](https://github.com/ghostty-org/ghostty) · [Eugeny/tabby](https://github.com/Eugeny/tabby) · [xpipe-io/xpipe](https://github.com/xpipe-io/xpipe) · [gnmyt/Nexterm](https://github.com/gnmyt/Nexterm) · [Gu1llaum-3/sshm](https://github.com/Gu1llaum-3/sshm)
</details>

---

*План составлен на основе автоматического анализа starred-репозиториев профиля. Обновляй его каждую пятницу по итогам ретро и по вопросам с реальных собеседований.*
