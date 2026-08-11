# Курс DevOps: уроки с практикой

Не видеокурс и не пересказ документации. Каждый урок устроен одинаково: короткая теория, потом практика, которую ты выполняешь руками в терминале, потом проверка результата и типичная ошибка. В конце — номера вопросов [тренажёра](qa-trainer.html), которые этот урок закрывает: прошёл урок — иди переставь себе оценку.

**Правила, без которых курс не работает.**

1. **Читать без терминала бессмысленно.** Урок считается пройденным, когда выполнена практика, а не когда прочитан текст.
2. **Один урок за раз.** Отметил галочку — закрыл ноутбук. Три урока подряд забываются к утру.
3. **Ломать специально.** В каждом уроке есть шаг «сломай и почини». Это не украшение: на собеседовании спрашивают именно про поломки.
4. **Не искать идеальную среду.** Всё, что нужно — Linux (или Docker) и `kubectl` с `k3d` начиная с двенадцатого урока. Облачный аккаунт не нужен нигде.

Порядок один: junior целиком, потом middle, потом senior. Если junior кажется скучным — прогони его на скорость, но прогони: провал на базовом вопросе стоит дороже, чем незнание senior-темы.

---

## Грейд junior — фундамент

Двенадцать уроков. Цель — не «узнать про Linux», а уметь за минуту ответить на вопрос «сервис не работает, что смотришь» и показать это руками.

### 1. Рабочее место, которое можно ломать

`Грейд` junior
`Время` 30 минут
`Вопросы` 195, 196, 44

`Зачем` Сделать себе песочницу, где не страшно удалить лишнее, и больше не бояться экспериментов.

**Теория.** Учиться на рабочем ноутбуке страшно, поэтому люди читают вместо того, чтобы делать. Решение — одноразовый контейнер: запустил, сломал, выбросил, запустил заново. Контейнер — это не виртуальная машина: он использует ядро хоста, а изоляцию даёт через namespaces и cgroups. Отсюда его главное свойство для учёбы — старт за секунду и удаление без следа.

`Практика`

```bash
# 1. Одноразовая машина: выйдешь — исчезнет (--rm)
docker run --rm -it --name lab ubuntu:24.04 bash

# внутри контейнера
apt-get update && apt-get install -y procps iproute2 curl less vim
ps aux
exit

# 2. Тот же контейнер, но переживающий выход
docker run -dit --name lab ubuntu:24.04 bash
docker exec -it lab bash
# ... поработал, вышел ...
docker stop lab && docker start lab && docker exec -it lab bash

# 3. Посмотреть, чем контейнер отличается от хоста
hostname                    # внутри
cat /proc/1/cmdline; echo   # PID 1 — это bash, а не systemd
ls /                        # свой корень
```

Теперь сломай и починь: удали `/etc/hosts` внутри контейнера, проверь, что сломалось (`ping google.com`), и восстанови контейнер одной командой — `docker rm -f lab` и заново `docker run`. Это и есть смысл одноразовой среды.

`Проверка` Ты можешь за десять секунд получить чистый Linux и не думаешь «а если я сломаю систему». Объясни вслух разницу между образом и контейнером: образ — неизменяемый шаблон из слоёв, контейнер — запущенный процесс с writable-слоем поверх.

`Типичная ошибка` Учиться в контейнере `alpine` и потом удивляться, что на сервере другие команды: в Alpine — BusyBox, у которого урезанные `ps`, `grep`, `awk`. Для учёбы бери `ubuntu` или `debian`, они ближе к тому, что стоит в проде.

### 2. Файлы, права и владельцы

`Грейд` junior
`Время` 40 минут
`Вопросы` 166, 167, 8, 23

`Зачем` Перестать угадывать `chmod 777` и понимать, почему сервис не читает свой конфиг.

**Теория.** Права — это три группы по три бита: владелец, группа, остальные. `r=4`, `w=2`, `x=1`. Для каталога `x` — это право войти внутрь, а не «выполнить»: без него `ls` по пути не работает, даже если файл читаемый. Есть четвёртая цифра: `4` — SUID (процесс запускается с правами владельца файла), `2` — SGID, `1` — sticky bit (в каталоге удалять файл может только его владелец — так устроен `/tmp`). `umask` — маска, которая вычитается из прав по умолчанию у новых файлов.

`Практика`

```bash
mkdir -p ~/lab/perm && cd ~/lab/perm
touch a.txt && mkdir sub
ls -l                      # разобрать вывод по столбцам: права, ссылки, владелец, группа, размер, дата

# отнять x у каталога и увидеть последствия
chmod 644 sub && ls sub/    # Permission denied — хотя r стоит
chmod 755 sub && ls sub/    # снова работает

# umask
umask                       # обычно 0022
touch b.txt && ls -l b.txt  # 644, потому что 666 - 022
umask 077 && touch c.txt && ls -l c.txt   # 600: файл видит только владелец

# особые биты
ls -l /usr/bin/passwd       # rws — SUID, поэтому обычный юзер меняет /etc/shadow
ls -ld /tmp                 # rwt — sticky bit
sudo chmod 2775 sub && ls -ld sub   # SGID: новые файлы наследуют группу каталога

# типы файлов
ls -l /dev/null /dev/sda /etc/os-release 2>/dev/null   # c, b, -
ln -s a.txt link.txt && ln a.txt hard.txt && ls -li     # symlink и hardlink: сравни inode
```

`Проверка` Объясни вслух, что делает `chmod 2755`, и почему `chmod -R 777 /var/www` — это не «починил доступ», а «выключил защиту». Удали `a.txt` и проверь, что `hard.txt` остался, а `link.txt` сломался — и скажи почему.

`Типичная ошибка` Путать права на файл с правами на путь к нему. Файл `640` в каталоге `700`, принадлежащем root, недоступен никому, кроме root, независимо от прав самого файла.

### 3. Поиск: find, grep, awk, sed

`Грейд` junior
`Время` 45 минут
`Вопросы` 168, 169, 24

`Зачем` Находить причину в логах за минуту, а не листать файл глазами.

**Теория.** Разделение труда: `find` ищет **файлы** по свойствам (имя, размер, время, владелец), `grep` ищет **строки** по шаблону, `awk` работает со строкой как с набором **полей** и умеет считать, `sed` **меняет** текст потоком. Девяносто процентов задач закрываются связкой «найти файлы → отфильтровать строки → посчитать по полю».

`Практика`

```bash
mkdir -p ~/lab/logs && cd ~/lab/logs
# сгенерировать похожий на настоящий access-лог
for i in $(seq 1 500); do
  code=$(shuf -e 200 200 200 200 301 404 500 502 -n1)
  ip="10.0.0.$((RANDOM%20))"
  echo "$ip - - [11/Aug/2026:10:$((RANDOM%60)):00] \"GET /api/v$((RANDOM%3)) HTTP/1.1\" $code $((RANDOM%5000))"
done > access.log

# find: что искать и где
find . -name "*.log" -size +1k -mmin -60
find /var/log -type f -size +10M 2>/dev/null

# grep: сколько пятисоток и какие именно
grep -c ' 500 ' access.log
grep -E ' (500|502) ' access.log | head -3
grep -v ' 200 ' access.log | wc -l     # инверсия

# awk: считать по полю
awk '{print $9}' access.log | sort | uniq -c | sort -rn        # распределение кодов
awk '$9>=500 {print $1}' access.log | sort | uniq -c | sort -rn # кто получает ошибки
awk '{sum+=$11} END {print "средний размер:", sum/NR}' access.log

# sed: заменить, не открывая редактор
sed 's/GET/POST/' access.log | head -2      # в поток
sed -i.bak 's/HTTP\/1.1/HTTP\/2/' access.log && ls   # на месте, с бэкапом
```

Теперь задача на время: одной строкой найди IP, который дал больше всего ошибок 5xx. Проверь себя: `awk '$9>=500{c[$1]++} END{for(i in c) print c[i], i}' access.log | sort -rn | head -1`.

`Проверка` Ты можешь без подсказки посчитать распределение кодов ответа в незнакомом логе и назвать топ-3 источника ошибок. Это буквально вопрос с собеседования «разбери этот вывод».

`Типичная ошибка` `cat file | grep x` вместо `grep x file`, и `grep` там, где нужен `awk`. Второе хуже: считать поля через `cut` и `grep` в три этапа — признак того, что человек не умеет `awk`.

### 4. Процессы, сигналы, нагрузка

`Грейд` junior
`Время` 40 минут
`Вопросы` 3, 4, 5, 6

`Зачем` Отвечать на «сервер тормозит» действиями, а не перезагрузкой.

**Теория.** Процесс завершают сигналом. `SIGTERM` (15) — просьба закрыться: приложение успевает сбросить буферы, закрыть соединения, снять блокировки. `SIGKILL` (9) — казнь ядром: процесс не получает управление вообще, поэтому теряет данные и оставляет мусор. Зомби — процесс, который завершился, но его код возврата не забрал родитель; сам он ресурсов не ест, но говорит о баге в родителе. Load average — среднее число процессов, готовых работать или ждущих диск, за 1, 5 и 15 минут; сравнивать надо с числом ядер: 10 на 16 ядрах — норма, 10 на двух — беда.

`Практика`

```bash
nproc                       # сколько ядер — без этого числа load average бессмыслен
uptime                      # три числа: тренд важнее абсолютного значения

# кто ест CPU и память
ps aux --sort=-%cpu | head -5
ps aux --sort=-%mem | head -5
top -b -n1 | head -15       # в интерактивном top: M — по памяти, P — по CPU, 1 — по ядрам

# сигналы вживую
sleep 300 &
PID=$!
kill -l | head -3           # список сигналов
kill -TERM $PID             # вежливо
jobs

# что делает процесс прямо сейчас
sleep 300 &
sudo strace -p $! 2>&1 | head -5   # видно, что висит в nanosleep
kill %2

# создать нагрузку и увидеть её
yes > /dev/null & yes > /dev/null &
sleep 5; uptime              # load average пошёл вверх
kill %1 %2

# состояния процессов: D — ждёт диск, Z — зомби
ps -eo pid,stat,comm | awk '$2 ~ /^[DZ]/'
```

`Проверка` Расскажи вслух порядок действий на «сервер тормозит»: `uptime` и `nproc` → что за нагрузка (CPU, память, диск, сеть) → кто её создаёт → что изменилось за последний час. Именно порядок, а не список команд, — то, что оценивают.

`Типичная ошибка` `kill -9` как первая реакция. У баз данных и брокеров это прямой путь к повреждённым данным и долгому восстановлению. Сначала `SIGTERM`, потом ждём, и только если процесс висит в необрываемом состоянии — `-9`.

### 5. Диск, inode и память

`Грейд` junior
`Время` 45 минут
`Вопросы` 173, 187, 2, 22, 13, 11

`Зачем` Разобрать самую частую аварию: «на диске нет места», в том числе её злую версию, когда файлов нет.

**Теория.** `df` спрашивает у файловой системы, сколько занято, `du` считает по дереву каталогов. Расхождение обычно означает удалённый, но открытый процессом файл: ссылки на него нет, места он не освобождает, потому что дескриптор ещё открыт. Отдельная поломка — кончились inode: место есть, а файл не создать, потому что закончились «учётные карточки» файлов. Память: в `free -h` смотреть надо на `available`, а не на `free` — ядро специально занимает свободную память кэшем и отдаёт её приложениям по требованию.

`Практика`

```bash
df -h                       # места
df -i                       # inode — отдельная колонка, о которой забывают
du -xh --max-depth=1 / 2>/dev/null | sort -h | tail   # где занято, не пересекая ФС

# воспроизвести расхождение df и du
cd /tmp && dd if=/dev/zero of=big bs=1M count=200
tail -f big > /dev/null &          # процесс держит файл открытым
rm big                              # файла нет...
df -h /tmp                          # ...а место занято
sudo lsof +L1 | head                # вот виновник: ссылок 0, дескриптор открыт
kill %1 && df -h /tmp               # место вернулось без перезагрузки

# кончились inode
mkdir /tmp/inodes && cd /tmp/inodes
for i in $(seq 1 20000); do : > f$i; done
df -i /tmp | tail -1                # число файлов выросло, место почти не изменилось
cd /tmp && rm -rf inodes

# память
free -h                             # available — единственная честная цифра
cat /proc/meminfo | head -5
dmesg -T | grep -i -E 'killed process|out of memory' | tail   # следы OOM killer
```

`Проверка` Ты можешь освободить место на проде, не перезагружая сервер, и объяснить, почему `df` и `du` расходятся. Отдельно — назвать три причины «нет места»: реально занято, кончились inode, удалённый открытый файл.

`Типичная ошибка` Ответ «перезагрузил, помогло». Помогло потому, что перезапуск закрыл дескриптор; причина осталась — скорее всего, logrotate без `copytruncate` или без сигнала приложению.

### 6. systemd: свой сервис и его логи

`Грейд` junior
`Время` 45 минут
`Вопросы` 179, 9, 20, 16

`Зачем` Уметь завести сервис так, чтобы он поднимался после перезагрузки и падения, и читать, почему он не поднялся.

**Теория.** systemd управляет юнитами и строит граф зависимостей, а не запускает скрипты по номерам, как SysV. Ключевые поля: `After` — порядок, `Wants`/`Requires` — зависимость (жёсткая или мягкая), `Type` — как systemd понимает, что сервис запустился (`simple` — сразу, `notify` — по сигналу от приложения, `forking` — по уходу в фон), `Restart` — политика перезапуска, `ExecStart` — что запускать. Логи пишутся в journald, и это преимущество: `journalctl -u сервис` покажет и вывод приложения, и системные сообщения о нём в одной ленте.

`Практика`

```bash
# простое приложение
sudo tee /usr/local/bin/hello.sh >/dev/null <<'EOF'
#!/bin/bash
while true; do echo "жив, $(date +%T)"; sleep 5; done
EOF
sudo chmod +x /usr/local/bin/hello.sh

sudo tee /etc/systemd/system/hello.service >/dev/null <<'EOF'
[Unit]
Description=Учебный сервис
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
ExecStart=/usr/local/bin/hello.sh
Restart=on-failure
RestartSec=3
User=nobody
# минимальный харденинг: сервису не нужен весь диск и не нужны новые привилегии
NoNewPrivileges=true
ProtectSystem=strict
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable --now hello
systemctl status hello --no-pager
journalctl -u hello -n 10 --no-pager

# сломать и прочитать причину
sudo sed -i 's|/usr/local/bin/hello.sh|/usr/local/bin/net.sh|' /etc/systemd/system/hello.service
sudo systemctl daemon-reload && sudo systemctl restart hello
systemctl status hello --no-pager        # exit code 203/EXEC — не нашёл файл
journalctl -u hello -p err -n 5 --no-pager
sudo sed -i 's|/usr/local/bin/net.sh|/usr/local/bin/hello.sh|' /etc/systemd/system/hello.service
sudo systemctl daemon-reload && sudo systemctl restart hello

# полезное в разборе
systemctl list-units --failed
systemctl cat hello                      # итоговый юнит со всеми override
journalctl -u hello --since "10 min ago"
journalctl -b -p err                     # ошибки с этой загрузки
```

`Проверка` Ты можешь с нуля написать юнит, объяснить `Type=simple` против `notify` и разницу `Wants` и `Requires`, и найти причину невзлетевшего сервиса за две команды.

`Типичная ошибка` `Restart=always` на сервисе, который падает из-за неверного конфига: systemd будет перезапускать его вечно, а в мониторинге это выглядит как «сервис флапает». `on-failure` плюс `StartLimitBurst` честнее — сервис уйдёт в failed, и это будет видно.

### 7. Сеть руками: когда ping не отвечает

`Грейд` junior
`Время` 50 минут
`Вопросы` 177, 178, 176, 192, 10, 31

`Зачем` Проверять доступность сервиса, а не «пинговать» — в проде ICMP закрыт почти везде.

**Теория.** «Не работает» — это как минимум пять разных проблем: не резолвится имя, не открыт порт, TCP есть но приложение не отвечает, отвечает ошибкой, отвечает медленно. Проверять надо по слоям снизу вверх, каждый раз получая однозначный ответ. `ping` проверяет только ICMP, который часто запрещён политикой, — его отсутствие ничего не говорит о сервисе.

`Практика`

```bash
# 1. Имя
dig +short github.com
dig github.com A +noall +answer      # TTL видно в выводе — важно для понимания кэша
getent hosts github.com              # так резолвит система, а не только dig

# 2. Порт
timeout 3 bash -c '</dev/tcp/github.com/443' && echo "порт открыт" || echo "порт закрыт"
nc -zv github.com 443 2>&1 | tail -1

# 3. Приложение
curl -sS -o /dev/null -w 'код %{http_code}, dns %{time_namelookup}s, connect %{time_connect}s, tls %{time_appconnect}s, всего %{time_total}s\n' https://github.com

# 4. Что слушает локально и кто это
ss -tulpn | head
ss -tan state established | head     # активные соединения
ss -tan state time-wait | wc -l      # много TIME_WAIT — отдельный разговор

# 5. Маршрут и путь
ip -brief addr; ip route
mtr -rwc 5 1.1.1.1 2>/dev/null || traceroute -n 1.1.1.1

# 6. Видеть пакеты своими глазами
sudo tcpdump -ni any -c 5 'tcp port 443'   # в другом окне: curl https://github.com

# 7. Сломать резолв и починить
echo "127.0.0.1 github.com" | sudo tee -a /etc/hosts
curl -sS -m 3 https://github.com ; echo "код возврата: $?"
sudo sed -i '/github.com/d' /etc/hosts
```

`Проверка` Проговори последовательность: имя → порт → рукопожатие TLS → ответ приложения → задержка, и назови команду для каждого шага. Отдельно: какие порты знаешь наизусть (22, 53, 80, 443, 3306, 5432, 6379, 9090, 6443).

`Типичная ошибка` Останавливаться на «пинг не идёт, значит сеть». Правильный ответ на собеседовании начинается со слов «пинг мало о чём говорит, проверю порт и ответ приложения».

### 8. nginx как reverse proxy и TLS

`Грейд` junior
`Время` 45 минут
`Вопросы` 181, 182, 34

`Зачем` Поставить перед приложением прокси с HTTPS — это половина типовых задач в вакансиях на инфраструктуру.

**Теория.** Reverse proxy принимает запрос от клиента и передаёт его наверх, к приложению: терминирует TLS, распределяет нагрузку, отдаёт статику, добавляет заголовки. Приложение при этом видит соединение от прокси, а не от клиента, — поэтому реальный IP и схему нужно передавать заголовками `X-Forwarded-For` и `X-Forwarded-Proto`, иначе приложение будет считать всех клиентов одним адресом и генерировать `http://` ссылки. Балансировка на L7 (nginx видит URL, метод, заголовки) отличается от L4 (виден только адрес и порт) ценой: L7 умнее, L4 быстрее.

`Практика`

```bash
# приложение-заглушка, которое показывает полученные заголовки
docker run -d --name app -p 8080:80 traefik/whoami

sudo tee /etc/nginx/conf.d/lab.conf >/dev/null <<'EOF'
upstream app_backend {
    server 127.0.0.1:8080;
    keepalive 16;
}

server {
    listen 80;
    server_name lab.local;

    location /healthz { return 200 "ok\n"; }

    location / {
        proxy_pass http://app_backend;
        proxy_http_version 1.1;
        proxy_set_header Host              $host;
        proxy_set_header X-Real-IP         $remote_addr;
        proxy_set_header X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 2s;
        proxy_read_timeout   10s;
    }
}
EOF

sudo nginx -t                     # проверять конфиг ДО перезагрузки — всегда
sudo systemctl reload nginx       # reload, а не restart: без обрыва соединений
curl -H 'Host: lab.local' localhost/healthz
curl -H 'Host: lab.local' localhost/ | grep -i forwarded

# TLS: сначала свой сертификат, чтобы понять механику
sudo openssl req -x509 -nodes -days 30 -newkey rsa:2048 \
  -keyout /etc/ssl/private/lab.key -out /etc/ssl/certs/lab.crt \
  -subj "/CN=lab.local"
openssl x509 -in /etc/ssl/certs/lab.crt -noout -subject -dates   # что внутри и до когда
```

Добавь в конфиг второй `server` на `listen 443 ssl;` с `ssl_certificate` и `ssl_certificate_key`, снова `nginx -t`, `reload`, и проверь `curl -k -H 'Host: lab.local' https://localhost/healthz`. В проде вместо самоподписанного — `certbot --nginx`, но механику надо понимать без него.

`Проверка` Ты можешь объяснить, зачем `X-Forwarded-For`, чем `reload` отличается от `restart`, и как проверить срок действия сертификата одной командой.

`Типичная ошибка` Перезапускать nginx без `nginx -t`. Ошибка в конфиге — и сервис не поднимется, а ты об этом узнаешь от мониторинга. Второе по частоте: забыть `proxy_set_header Host`, после чего приложение с виртуальными хостами отдаёт не тот сайт.

### 9. SSH: ключи, конфиг, харденинг

`Грейд` junior
`Время` 35 минут
`Вопросы` 180, 189

`Зачем` Перестать вводить пароли и закрыть самый атакуемый порт в интернете.

**Теория.** Аутентификация по ключу — это асимметричная криптография: приватный ключ остаётся у тебя, публичный лежит на сервере в `authorized_keys`. Сервер отправляет челлендж, клиент подписывает его приватным ключом — пароль не передаётся вообще, поэтому его нельзя подобрать или подслушать. Тип ключа: `ed25519` короче и быстрее RSA при большей стойкости, RSA нужен только для совместимости со старым софтом. `~/.ssh/config` избавляет от простыней флагов и умеет прыгать через bastion одной строкой.

`Практика`

```bash
# ключ
ssh-keygen -t ed25519 -C "nurekella@laptop" -f ~/.ssh/id_lab
ls -l ~/.ssh/id_lab*            # приватный обязан быть 600

# положить публичный на сервер (в лабе — на localhost)
ssh-copy-id -i ~/.ssh/id_lab.pub localhost
cat ~/.ssh/authorized_keys

# удобный конфиг
cat >> ~/.ssh/config <<'EOF'
Host lab
    HostName localhost
    User     nurekella
    IdentityFile ~/.ssh/id_lab
    IdentitiesOnly yes

# доступ во внутреннюю сеть через бастион одной командой
Host db-prod
    HostName 10.0.5.20
    User     nurekella
    ProxyJump bastion.example.com
EOF
chmod 600 ~/.ssh/config
ssh lab 'hostname; whoami'

# харденинг сервера
sudo tee /etc/ssh/sshd_config.d/99-lab.conf >/dev/null <<'EOF'
PermitRootLogin no
PasswordAuthentication no
KbdInteractiveAuthentication no
MaxAuthTries 3
AllowGroups ssh-users
ClientAliveInterval 300
EOF
sudo sshd -t                    # проверить конфиг, иначе можно потерять доступ
sudo groupadd -f ssh-users && sudo usermod -aG ssh-users "$USER"
sudo systemctl reload ssh
```

`Проверка` Ты заходишь по ключу без пароля, `ssh db-prod` работает через бастион, а вход по паролю и под root запрещён. Объясни вслух, почему запрет пароля важнее сложного пароля.

`Типичная ошибка` Применить харденинг и закрыть себе доступ. Правило: **не закрывай текущую сессию, пока новым подключением не проверил, что вход работает.** И всегда `sshd -t` перед reload.

### 10. Git на каждый день

`Грейд` junior
`Время` 40 минут
`Вопросы` 193, 194, 41, 42, 38

`Зачем` Уверенно отвечать на «как отменить изменения» — вопрос, на котором сыплется половина кандидатов.

**Теория.** Три области: рабочий каталог, индекс (staging) и история коммитов. `add` переносит из каталога в индекс, `commit` — из индекса в историю. Отмена зависит от того, где изменение: в каталоге — `restore`, в индексе — `restore --staged`, в истории — `revert` (новый коммит, безопасно для общих ветвей) или `reset` (сдвиг указателя, переписывает историю). `fetch` только скачивает состояние удалённого репозитория, `pull` — это `fetch` плюс слияние, поэтому `pull` может неожиданно создать merge-коммит.

`Практика`

```bash
mkdir -p ~/lab/git && cd ~/lab/git && git init -b main
git config user.email you@example.com && git config user.name "You"

echo "v1" > app.txt && git add app.txt && git commit -m "первый коммит"
echo "мусор" >> app.txt
git diff                              # различия каталога и индекса
git restore app.txt                   # откатить незакоммиченное
cat app.txt

echo "v2" > app.txt && git add app.txt
git restore --staged app.txt          # убрать из индекса, оставив в файле
git status

# история
git add app.txt && git commit -m "v2"
git log --oneline --graph
git revert --no-edit HEAD             # безопасная отмена: новый коммит
git log --oneline

git reset --soft HEAD~1               # изменения остались в индексе
git reset --hard HEAD~1               # изменения уничтожены — только для своей ветки

# конфликт своими руками
git switch -c feature
echo "из feature" > app.txt && git commit -am "feature"
git switch main
echo "из main" > app.txt && git commit -am "main"
git merge feature                     # CONFLICT
git status                            # смотри, какие файлы
vim app.txt                           # убрать маркеры <<<<<<< ======= >>>>>>>
git add app.txt && git commit --no-edit

# страховка на все случаи
git reflog                            # тут видно даже то, что "потеряно" после reset
git stash && git stash list && git stash pop
git log -S "из main" --oneline        # когда появилась строка
git blame app.txt
```

`Проверка` Не подсматривая, скажи разницу `reset --soft/--mixed/--hard`, когда уместен `revert` вместо `reset`, и как вернуть коммит после `reset --hard` (ответ: `git reflog`).

`Типичная ошибка` `git reset --hard` в общей ветке. Историю переписали, у коллег расхождение, и починка занимает вечер. В общих ветвях — только `revert`.

### 11. Docker: свой образ и compose

`Грейд` junior
`Время` 50 минут
`Вопросы` 195, 196, 45, 47, 49, 55

`Зачем` Собрать образ, который не стыдно показать, и поднять два связанных сервиса одной командой.

**Теория.** Образ состоит из слоёв, каждая инструкция Dockerfile добавляет слой, слои кэшируются. Отсюда правило порядка: сначала то, что меняется редко (установка зависимостей), потом то, что меняется каждый коммит (код) — иначе кэш будет сбрасываться на каждой сборке. `CMD` — аргументы по умолчанию, их легко заменить при запуске; `ENTRYPOINT` — сама команда, она остаётся. Данные внутри контейнера живут в его writable-слое и исчезают вместе с ним: чтобы сохранить, нужен volume.

`Практика`

```bash
mkdir -p ~/lab/app && cd ~/lab/app
cat > app.py <<'EOF'
import os, http.server, socketserver
class H(http.server.BaseHTTPRequestHandler):
    def do_GET(s):
        s.send_response(200); s.end_headers()
        s.wfile.write(("привет из " + os.uname().nodename + "\n").encode())
socketserver.TCPServer(("", 8000), H).serve_forever()
EOF

cat > Dockerfile <<'EOF'
FROM python:3.12-slim
WORKDIR /app
# зависимости отдельным слоем — кэш не сбросится при правке кода
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
# не root: если процесс скомпрометируют, он не будет всесильным
RUN useradd -u 10001 -m appuser
USER 10001
EXPOSE 8000
ENTRYPOINT ["python", "app.py"]
EOF
: > requirements.txt

docker build -t lab-app:1 .
docker build -t lab-app:1 .          # второй раз — все слои из кэша
echo "# правка" >> app.py && docker build -t lab-app:2 .   # пересобрался только последний слой

docker run -d --name web -p 8000:8000 lab-app:2
curl localhost:8000
docker exec web id                    # 10001, не root
docker logs web | tail -3
docker image history lab-app:2        # слои и их размер

# данные и их потеря
docker exec web sh -c 'echo данные > /tmp/x' 2>/dev/null
docker rm -f web && docker run -d --name web -p 8000:8000 lab-app:2
docker exec web cat /tmp/x            # файла нет — writable-слой умер вместе с контейнером
docker volume create labdata
docker rm -f web
docker run -d --name web -p 8000:8000 -v labdata:/data lab-app:2
docker exec web sh -c 'echo данные > /data/x' && docker rm -f web
docker run -d --name web -p 8000:8000 -v labdata:/data lab-app:2 && docker exec web cat /data/x

# два сервиса вместе
cat > compose.yaml <<'EOF'
services:
  web:
    build: .
    ports: ["8000:8000"]
    environment:
      DB_HOST: db
    depends_on:
      db:
        condition: service_healthy
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_PASSWORD: labpass
    volumes: ["pgdata:/var/lib/postgresql/data"]
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      retries: 5
volumes:
  pgdata:
EOF
docker compose up -d
docker compose ps
docker compose exec web getent hosts db     # сервисы видят друг друга по имени
docker compose logs --tail 5 db
docker compose down                        # без -v данные тома остаются
```

`Проверка` Объясни, почему `COPY requirements.txt` идёт до `COPY app.py`, чем `CMD` отличается от `ENTRYPOINT`, и где живут данные, если тома нет. Проверь, что твой контейнер работает не от root.

`Типичная ошибка` `COPY . .` первой строкой: любая правка любого файла сбрасывает кэш, и сборка каждый раз идёт с нуля. Вторая — тег `latest` в проде: невозможно понять, что именно запущено, и откат превращается в угадывание.

### 12. Kubernetes: первый кластер и первое приложение

`Грейд` junior
`Время` 60 минут
`Вопросы` 197, 198, 199, 200, 66, 75, 65

`Зачем` Пройти путь от пустого кластера до работающего приложения с конфигом, секретом и доступом снаружи.

**Теория.** Pod — минимальная единица планирования: один или несколько контейнеров с общими сетевым пространством и томами. Поды одноразовы, поэтому руками их не создают: Deployment описывает желаемое состояние («три реплики такого-то образа»), создаёт ReplicaSet, а тот следит за числом подов. Service даёт стабильное имя и адрес, потому что IP пода меняется при каждом пересоздании. ConfigMap и Secret отделяют конфигурацию от образа — один образ едет во все окружения, меняются только они.

`Практика`

```bash
# кластер на ноутбуке
k3d cluster create lab --agents 2
kubectl get nodes -o wide
kubectl cluster-info

# первое приложение декларативно
mkdir -p ~/lab/k8s && cd ~/lab/k8s
cat > app.yaml <<'EOF'
apiVersion: v1
kind: ConfigMap
metadata: { name: app-config }
data:
  GREETING: "привет из ConfigMap"
---
apiVersion: v1
kind: Secret
metadata: { name: app-secret }
stringData:
  TOKEN: "s3cr3t"
---
apiVersion: apps/v1
kind: Deployment
metadata: { name: web }
spec:
  replicas: 3
  selector:
    matchLabels: { app: web }
  template:
    metadata:
      labels: { app: web }
    spec:
      containers:
        - name: whoami
          image: traefik/whoami:v1.10
          ports: [{ containerPort: 80 }]
          envFrom:
            - configMapRef: { name: app-config }
            - secretRef:    { name: app-secret }
          resources:
            requests: { cpu: 10m, memory: 16Mi }
            limits:   { cpu: 200m, memory: 64Mi }
---
apiVersion: v1
kind: Service
metadata: { name: web }
spec:
  selector: { app: web }
  ports: [{ port: 80, targetPort: 80 }]
EOF

kubectl apply -f app.yaml
kubectl get deploy,rs,pod,svc
kubectl describe deploy web | head -25
kubectl exec deploy/web -- env | grep -E 'GREETING|TOKEN'

# команды, которыми живёшь каждый день
kubectl get pods -o wide
kubectl logs deploy/web --tail=5
kubectl exec -it deploy/web -- sh -c 'wget -qO- localhost'
kubectl port-forward svc/web 8080:80 &
curl -s localhost:8080 | head -3; kill %1

# самоисцеление: удали под и смотри
kubectl delete pod -l app=web --wait=false
kubectl get pods -w --timeout=30s      # Ctrl+C — ReplicaSet поднял новый

# обновление и откат
kubectl set image deploy/web whoami=traefik/whoami:v1.9
kubectl rollout status deploy/web
kubectl rollout history deploy/web
kubectl rollout undo deploy/web
kubectl get rs                          # старый ReplicaSet остался для откатов

# правда про Secret
kubectl get secret app-secret -o jsonpath='{.data.TOKEN}' | base64 -d; echo
```

`Проверка` Ты можешь поднять кластер и приложение с нуля за десять минут, объяснить связку Deployment → ReplicaSet → Pod, назвать, что произойдёт при удалении пода, и сказать, почему Secret в base64 — это не шифрование.

`Типичная ошибка` Создавать поды напрямую (`kubectl run`) и потом удивляться, что после падения узла приложение не вернулось. И `kubectl edit` в проде: изменение живёт до следующего `apply` из git, а потом бесследно исчезает.

---

## Грейд middle — эксплуатация

Четырнадцать уроков. Здесь начинается то, за что платят: не «поднять», а «эксплуатировать» — разбирать падения, обновлять без простоя, измерять надёжность.

### 13. Docker всерьёз: тонкий образ и сборка в CI

`Грейд` middle
`Время` 50 минут
`Вопросы` 48, 54, 51, 57, 152

`Зачем` Уменьшить образ в разы и научиться отвечать на «почему у тебя образ 1.2 ГБ».

**Теория.** Multi-stage сборка разделяет окружение сборки и окружение запуска: в первой стадии есть компилятор, зависимости и кэш, в финальный образ переносится только артефакт. Это одновременно и размер, и безопасность: чем меньше в образе программ, тем меньше поверхность атаки и меньше CVE в отчёте сканера. Тег `latest` в проде ломает воспроизводимость — один и тот же манифест в разное время даст разные образы; фиксировать надо тег версии, а в критичных местах digest (`image@sha256:…`), потому что тег можно перезаписать, а digest — нет.

`Практика`

```bash
mkdir -p ~/lab/thin && cd ~/lab/thin
cat > main.go <<'EOF'
package main
import ("fmt"; "net/http")
func main() {
  http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) { fmt.Fprintln(w, "ok") })
  http.ListenAndServe(":8080", nil)
}
EOF

# как делать не надо
cat > Dockerfile.fat <<'EOF'
FROM golang:1.23
WORKDIR /src
COPY . .
RUN go build -o app main.go
CMD ["/src/app"]
EOF

# как надо
cat > Dockerfile <<'EOF'
FROM golang:1.23 AS build
WORKDIR /src
COPY go.* ./
RUN go mod download || true
COPY . .
RUN CGO_ENABLED=0 go build -ldflags="-s -w" -o /out/app main.go

FROM gcr.io/distroless/static:nonroot
COPY --from=build /out/app /app
USER 65532:65532
EXPOSE 8080
ENTRYPOINT ["/app"]
EOF
go mod init lab 2>/dev/null || true

docker build -f Dockerfile.fat -t lab:fat . && docker build -t lab:thin .
docker images | grep -E 'lab +(fat|thin)'        # разница обычно в 40-80 раз
dive lab:thin 2>/dev/null || docker image history lab:thin

# запуск и проверка, что не root
docker run -d --name thin -p 8081:8080 lab:thin && curl -s localhost:8081
docker inspect -f '{{.Config.User}}' thin

# digest вместо тега
docker pull nginx:1.27
docker inspect --format='{{index .RepoDigests 0}}' nginx:1.27

# сканер: посмотреть, что сокращение образа даёт по CVE
trivy image --severity HIGH,CRITICAL lab:fat 2>/dev/null | tail -5
trivy image --severity HIGH,CRITICAL lab:thin 2>/dev/null | tail -5
```

`Проверка` Твой финальный образ меньше 20 МБ, работает не от root, и ты можешь объяснить, что попало в него, а что осталось в стадии сборки. Назови три способа уменьшить образ: multi-stage, минимальная база, `.dockerignore` и объединение слоёв с очисткой кэша пакетного менеджера.

`Типичная ошибка` `RUN apt-get install` и `RUN apt-get clean` разными слоями: удалённые файлы остаются в предыдущем слое, размер не уменьшается. Чистить надо в той же инструкции, что и устанавливать.

### 14. Probes, requests, limits и QoS

`Грейд` middle
`Время` 50 минут
`Вопросы` 60, 61, 153

`Зачем` Понять два механизма, которые чаще всего настраивают неправильно и потом получают падения под нагрузкой.

**Теория.** Три пробы отвечают на три разных вопроса. `startup` — «приложение ещё поднимается, не мешайте»: пока она не прошла, остальные не выполняются. `readiness` — «можно ли давать трафик»: провал убирает под из endpoints Service, но контейнер не перезапускается. `liveness` — «жив ли процесс»: провал ведёт к рестарту. Перепутать liveness и readiness — классическая авария: медленный ответ под нагрузкой валит liveness, kubelet перезапускает поды, нагрузка идёт на оставшиеся, они тоже перестают отвечать — каскад.

`requests` — то, по чему планировщик выбирает узел и что гарантировано поду. `limits` — жёсткий потолок: по CPU это throttling (процесс замедляется), по памяти — OOMKill (контейнер убивают). Отсюда QoS-классы: `Guaranteed` (requests == limits для всех контейнеров) вытесняется последним, `Burstable` (requests < limits) — посередине, `BestEffort` (ничего не указано) — первым.

`Практика`

```bash
cd ~/lab/k8s
cat > probes.yaml <<'EOF'
apiVersion: apps/v1
kind: Deployment
metadata: { name: probed }
spec:
  replicas: 2
  selector: { matchLabels: { app: probed } }
  template:
    metadata: { labels: { app: probed } }
    spec:
      containers:
        - name: app
          image: traefik/whoami:v1.10
          ports: [{ containerPort: 80 }]
          startupProbe:
            httpGet: { path: /, port: 80 }
            failureThreshold: 30
            periodSeconds: 2
          readinessProbe:
            httpGet: { path: /, port: 80 }
            periodSeconds: 5
            failureThreshold: 2
          livenessProbe:
            httpGet: { path: /, port: 80 }
            periodSeconds: 10
            failureThreshold: 3
          resources:
            requests: { cpu: 50m, memory: 32Mi }
            limits:   { cpu: 50m, memory: 32Mi }   # == requests → Guaranteed
EOF
kubectl apply -f probes.yaml && kubectl rollout status deploy/probed
kubectl get pod -l app=probed -o jsonpath='{.items[0].status.qosClass}'; echo

# readiness убирает под из трафика, не перезапуская его
kubectl expose deploy probed --port 80 2>/dev/null
kubectl get endpoints probed
POD=$(kubectl get pod -l app=probed -o name | head -1)
kubectl exec $POD -- sh -c 'kill 1' 2>/dev/null || true
kubectl get pod -l app=probed          # RESTARTS вырос
kubectl get endpoints probed           # на время рестарта адрес ушёл из endpoints

# OOMKill вживую
cat > oom.yaml <<'EOF'
apiVersion: v1
kind: Pod
metadata: { name: hungry }
spec:
  containers:
    - name: eat
      image: python:3.12-slim
      command: ["python","-c","a=bytearray(200*1024*1024); import time; time.sleep(300)"]
      resources:
        limits: { memory: 64Mi }
EOF
kubectl apply -f oom.yaml
sleep 12
kubectl get pod hungry
kubectl describe pod hungry | grep -A3 -E 'Last State|Reason'   # OOMKilled, exit 137

# CPU throttling: контейнер не убивают, он просто медленный
kubectl run cpu --image=busybox --restart=Never \
  --overrides='{"spec":{"containers":[{"name":"cpu","image":"busybox","command":["sh","-c","time dd if=/dev/zero of=/dev/null bs=1M count=200000"],"resources":{"limits":{"cpu":"100m"}}}]}}'
sleep 15 && kubectl logs cpu
kubectl delete pod hungry cpu --ignore-not-found
```

`Проверка` Объясни на память: что будет, если liveness ссылается на эндпоинт, который зависит от базы (ответ: падение базы вызовет рестарт всех подов, хотя приложение живо). И почему `Guaranteed` важен для баз данных.

`Типичная ошибка` Ставить `limits` по памяти равным `requests` «для порядка» на JVM-приложениях без настройки heap — приложение видит память узла, а не лимит, и стабильно получает OOMKill.

### 15. Разбор падений: CrashLoopBackOff и Pending

`Грейд` middle
`Время` 50 минут
`Вопросы` 62, 63, 56, 78

`Зачем` Довести до автоматизма два самых частых состояния — их дают разбирать на живом кластере на собеседовании.

**Теория.** `CrashLoopBackOff` — это не ошибка, а цикл: контейнер запустился, упал, kubelet ждёт с растущей задержкой (10с, 20с, 40с… до 5 минут) и пробует снова. Причина всегда внутри: код возврата и логи предыдущей попытки. `Pending` — под не назначен на узел: не хватает ресурсов, не подходят taints/affinity, нет PVC, или узлы не Ready. Разница принципиальна: `CrashLoopBackOff` — проблема приложения, `Pending` — проблема кластера или манифеста.

`Практика`

```bash
cd ~/lab/k8s
# 1. CrashLoopBackOff: неверная команда
kubectl run crash --image=busybox --restart=Always -- sh -c 'echo стартую; exit 1'
sleep 20
kubectl get pod crash
kubectl describe pod crash | grep -A5 'Last State'      # exit code
kubectl logs crash --previous                            # логи упавшей попытки — главное
kubectl get events --sort-by=.lastTimestamp | tail -5

# 2. CrashLoopBackOff: нет конфига
cat > needcfg.yaml <<'EOF'
apiVersion: v1
kind: Pod
metadata: { name: needcfg }
spec:
  containers:
    - name: app
      image: busybox
      command: ["sh","-c","cat /etc/app/config.yaml"]
      volumeMounts: [{ name: cfg, mountPath: /etc/app }]
  volumes:
    - name: cfg
      configMap: { name: missing-config }
EOF
kubectl apply -f needcfg.yaml && sleep 5
kubectl get pod needcfg                                  # ContainerCreating, не Crash
kubectl describe pod needcfg | tail -5                   # причина в Events: configmap not found
kubectl create configmap missing-config --from-literal=config.yaml="ok: true"
sleep 5 && kubectl logs needcfg

# 3. Pending: не хватает ресурсов
kubectl run huge --image=nginx --restart=Never \
  --overrides='{"spec":{"containers":[{"name":"huge","image":"nginx","resources":{"requests":{"cpu":"64","memory":"256Gi"}}}]}}'
kubectl get pod huge
kubectl describe pod huge | grep -A5 Events              # Insufficient cpu/memory
kubectl describe node | grep -A6 'Allocated resources'   # сколько реально осталось

# 4. Pending: taint без toleration
NODE=$(kubectl get nodes -o name | tail -1)
kubectl taint $NODE lab=only:NoSchedule
kubectl run tainted --image=nginx --restart=Never --overrides='{"spec":{"nodeSelector":{"kubernetes.io/hostname":"'$(basename $NODE)'"}}}'
kubectl describe pod tainted | grep -A3 Events           # had untolerated taint
kubectl taint $NODE lab=only:NoSchedule-

kubectl delete pod crash needcfg huge tainted --ignore-not-found
```

`Проверка` Проговори алгоритм за 30 секунд: `kubectl get pod` → `describe` (Events и Last State) → `logs --previous` → код возврата → гипотеза. И назови, что означают коды 137 (SIGKILL, обычно OOM), 143 (SIGTERM), 1 (ошибка приложения), 203 (не смог запустить бинарник).

`Типичная ошибка` Смотреть `kubectl logs` без `--previous` у падающего пода: текущая попытка ещё не успела ничего записать, и человек решает, что «логов нет».

### 16. Обновление без простоя и откат

`Грейд` middle
`Время` 45 минут
`Вопросы` 67, 94, 100, 84

`Зачем` Обновлять прод в рабочее время и уметь откатиться за одну команду.

**Теория.** Rolling update заменяет поды по частям: `maxUnavailable` — сколько можно потерять, `maxSurge` — сколько можно добавить сверх нормы. Простоя не будет, только если у пода есть readiness (иначе трафик пойдёт в неготовый под) и корректная обработка `SIGTERM` (иначе оборвутся текущие запросы). PodDisruptionBudget защищает от добровольных нарушений — дренажа узла при обновлении кластера: он не даёт вывести столько подов, чтобы сервис просел. Rolling не проверяет релиз на реальном трафике — для этого canary или blue-green.

`Практика`

```bash
cd ~/lab/k8s
cat > rolling.yaml <<'EOF'
apiVersion: apps/v1
kind: Deployment
metadata: { name: roll }
spec:
  replicas: 4
  strategy:
    type: RollingUpdate
    rollingUpdate: { maxUnavailable: 1, maxSurge: 1 }
  selector: { matchLabels: { app: roll } }
  template:
    metadata: { labels: { app: roll } }
    spec:
      terminationGracePeriodSeconds: 20
      containers:
        - name: app
          image: traefik/whoami:v1.10
          readinessProbe: { httpGet: { path: /, port: 80 }, periodSeconds: 2 }
          lifecycle:
            preStop:
              exec: { command: ["sh","-c","sleep 5"] }   # дать балансировщику убрать нас из endpoints
---
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata: { name: roll }
spec:
  minAvailable: 3
  selector: { matchLabels: { app: roll } }
EOF
kubectl apply -f rolling.yaml && kubectl rollout status deploy/roll

# наблюдать обновление
kubectl set image deploy/roll app=traefik/whoami:v1.9 && kubectl get pods -l app=roll -w --timeout=60s

# история и откат
kubectl rollout history deploy/roll
kubectl rollout undo deploy/roll && kubectl rollout status deploy/roll
kubectl describe deploy roll | grep Image

# сломанный релиз: rollout зависает, а не ломает прод
kubectl set image deploy/roll app=traefik/whoami:НЕТ-ТАКОГО-ТЕГА
sleep 15
kubectl get pods -l app=roll                 # новый под в ImagePullBackOff, старые работают
kubectl rollout status deploy/roll --timeout=10s ; echo "код возврата: $?"
kubectl rollout undo deploy/roll

# PDB в действии: дренаж узла
kubectl get pdb roll
kubectl drain $(kubectl get nodes -o name | tail -1 | cut -d/ -f2) --ignore-daemonsets --delete-emptydir-data --timeout=60s
kubectl get pods -l app=roll -o wide
kubectl uncordon $(kubectl get nodes -o name | tail -1 | cut -d/ -f2)
```

`Проверка` Объясни, зачем `preStop` со сном, если есть readiness (ответ: удаление из endpoints и остановка контейнера происходят параллельно, сон даёт балансировщику успеть). И что делает PDB при `drain`.

`Типичная ошибка` Считать, что rolling update сам по себе даёт нулевой простой. Без readiness и без обработки SIGTERM он даёт ровно то же, что и `kubectl delete pod`, только медленнее.

### 17. RBAC: выдать ровно столько прав, сколько нужно

`Грейд` middle
`Время` 45 минут
`Вопросы` 68, 69, 163, 140

`Зачем` Отвечать на «выдай приложению минимальные права» кодом, а не словами про best practices.

**Теория.** Четыре объекта: Role (права в namespace), ClusterRole (права на весь кластер), RoleBinding и ClusterRoleBinding (кому эти права). Субъект — ServiceAccount для приложений, User или Group для людей. Права аддитивны: запретить нельзя, можно только не дать. Проверять надо не глазами, а `kubectl auth can-i`, в том числе от имени сервис-аккаунта. `ServiceAccount` монтируется в под токеном, и приложение обращается к API с ним — поэтому «под с правами cluster-admin» означает «любой, кто выполнит код в этом поде, владеет кластером».

`Практика`

```bash
cd ~/lab/k8s
cat > rbac.yaml <<'EOF'
apiVersion: v1
kind: ServiceAccount
metadata: { name: reader, namespace: default }
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata: { name: pod-reader, namespace: default }
rules:
  - apiGroups: [""]
    resources: ["pods", "pods/log"]
    verbs: ["get", "list", "watch"]
  - apiGroups: [""]
    resources: ["configmaps"]
    resourceNames: ["app-config"]        # только один конкретный объект
    verbs: ["get"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata: { name: reader-can-read, namespace: default }
subjects: [{ kind: ServiceAccount, name: reader, namespace: default }]
roleRef: { kind: Role, name: pod-reader, apiGroup: rbac.authorization.k8s.io }
EOF
kubectl apply -f rbac.yaml

# проверка правами, а не надеждой
kubectl auth can-i list pods --as=system:serviceaccount:default:reader
kubectl auth can-i delete pods --as=system:serviceaccount:default:reader
kubectl auth can-i get configmap/app-config --as=system:serviceaccount:default:reader
kubectl auth can-i get configmap/other --as=system:serviceaccount:default:reader
kubectl auth can-i --list --as=system:serviceaccount:default:reader | head

# приложение с этим аккаунтом обращается к API само
kubectl run apiclient --image=curlimages/curl:8.10.1 --restart=Never \
  --overrides='{"spec":{"serviceAccountName":"reader"}}' -- sleep 3600
sleep 5
kubectl exec apiclient -- sh -c '
  T=$(cat /var/run/secrets/kubernetes.io/serviceaccount/token)
  curl -s --cacert /var/run/secrets/kubernetes.io/serviceaccount/ca.crt \
    -H "Authorization: Bearer $T" https://kubernetes.default/api/v1/namespaces/default/pods | head -c 120; echo
  curl -s -o /dev/null -w "\nудаление: %{http_code}\n" -X DELETE --cacert /var/run/secrets/kubernetes.io/serviceaccount/ca.crt \
    -H "Authorization: Bearer $T" https://kubernetes.default/api/v1/namespaces/default/pods/apiclient'

# кто в кластере всесилен — полезная проверка на новом месте
kubectl get clusterrolebindings -o json | \
  jq -r '.items[] | select(.roleRef.name=="cluster-admin") | .metadata.name + " → " + ([.subjects[]?.name] | join(","))' 2>/dev/null

kubectl delete pod apiclient --ignore-not-found
```

`Проверка` Ты можешь с нуля написать Role и RoleBinding, ограничить права одним конкретным ConfigMap через `resourceNames` и доказать результат через `auth can-i`. Объясни, чем Role отличается от ClusterRole и почему нет запрещающих правил.

`Типичная ошибка` Выдать `ClusterRole/edit` вместо Role в одном namespace, потому что «так быстрее заработало». На аудите это первое, что находят.

### 18. Сеть кластера: Service, DNS и NetworkPolicy

`Грейд` middle
`Время` 55 минут
`Вопросы` 64, 73, 81, 159, 161

`Зачем` Понимать, как запрос доходит до пода, и уметь закрыть namespace по умолчанию.

**Теория.** Service — это не прокси-процесс, а правило. kube-proxy (или eBPF в Cilium) программирует на каждом узле правила iptables/ipvs, которые подменяют адрес назначения на IP одного из готовых подов. Список готовых берётся из объекта EndpointSlice, который наполняется по селектору Service и readiness-пробам. Отсюда правило отладки: **пустые endpoints — значит, селектор не совпал с метками или поды не готовы**, и никакая настройка Service не поможет. DNS в кластере даёт имена вида `service.namespace.svc.cluster.local`. NetworkPolicy — это разрешающие правила: пока политик нет, разрешено всё; как только на под попала хотя бы одна политика, всё, что не разрешено, запрещено.

`Практика`

```bash
cd ~/lab/k8s
kubectl create ns shop 2>/dev/null
kubectl -n shop create deploy api --image=traefik/whoami:v1.10 --replicas=2
kubectl -n shop expose deploy api --port 80
kubectl -n shop run client --image=curlimages/curl:8.10.1 -- sleep 3600
sleep 8

# путь запроса
kubectl -n shop get svc api -o wide
kubectl -n shop get endpointslices -l kubernetes.io/service-name=api -o wide
kubectl -n shop exec client -- curl -s api | head -2
kubectl -n shop exec client -- nslookup api 2>/dev/null | tail -4
kubectl -n shop exec client -- curl -s api.shop.svc.cluster.local | head -2

# сломать селектор и увидеть пустые endpoints — это и есть задача «Service не отдаёт трафик»
kubectl -n shop patch svc api -p '{"spec":{"selector":{"app":"НЕВЕРНО"}}}'
kubectl -n shop get endpoints api                       # <none>
kubectl -n shop exec client -- curl -s -m 3 api ; echo "код: $?"
kubectl -n shop patch svc api -p '{"spec":{"selector":{"app":"api"}}}'
kubectl -n shop get endpoints api

# default deny и точечные разрешения
cat > netpol.yaml <<'EOF'
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata: { name: default-deny, namespace: shop }
spec:
  podSelector: {}
  policyTypes: [Ingress, Egress]
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata: { name: allow-dns, namespace: shop }
spec:
  podSelector: {}
  policyTypes: [Egress]
  egress:
    - to: [{ namespaceSelector: { matchLabels: { kubernetes.io/metadata.name: kube-system } } }]
      ports: [{ protocol: UDP, port: 53 }, { protocol: TCP, port: 53 }]
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata: { name: client-to-api, namespace: shop }
spec:
  podSelector: { matchLabels: { app: api } }
  policyTypes: [Ingress]
  ingress:
    - from: [{ podSelector: { matchLabels: { run: client } } }]
      ports: [{ protocol: TCP, port: 80 }]
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata: { name: client-egress-api, namespace: shop }
spec:
  podSelector: { matchLabels: { run: client } }
  policyTypes: [Egress]
  egress:
    - to: [{ podSelector: { matchLabels: { app: api } } }]
      ports: [{ protocol: TCP, port: 80 }]
EOF
kubectl apply -f netpol.yaml
kubectl -n shop exec client -- curl -s -m 5 api | head -2         # разрешено
kubectl -n shop exec client -- curl -s -m 5 https://github.com ; echo "во внешний мир: $?"

# отладка сети из пода со всеми инструментами
kubectl -n shop run shoot --rm -it --image=nicolaka/netshoot -- \
  sh -c 'dig +short api.shop.svc.cluster.local; nc -zv api 80; exit' 2>/dev/null
```

`Проверка` Объясни, где физически живёт «балансировщик» ClusterIP, назови первую команду при «Service не отвечает» (`kubectl get endpoints`), и напиши default deny по памяти. Отдельно: почему после default deny обязательно нужно разрешить DNS.

`Типичная ошибка` Применить default deny и забыть про DNS: приложение начинает падать с таймаутами на резолве, а в логах это выглядит как «база недоступна».

### 19. Хранилище: PV, PVC и StatefulSet

`Грейд` middle
`Время` 45 минут
`Вопросы` 74, 66, 128

`Зачем` Запускать в кластере то, что имеет состояние, и понимать, почему база — это не Deployment.

**Теория.** PVC — заявка приложения («нужно 5 ГБ с такими режимами доступа»), PV — конкретный том, StorageClass — правило, по которому том создаётся автоматически, CSI — драйвер, который умеет это делать у конкретного провайдера. Режимы доступа: `ReadWriteOnce` (один узел), `ReadOnlyMany`, `ReadWriteMany` (нужна сетевая ФС). `reclaimPolicy: Delete` удалит данные вместе с PVC — для баз это `Retain`. StatefulSet отличается от Deployment тремя вещами: стабильные имена (`db-0`, `db-1`), персональный PVC на каждую реплику и упорядоченные запуск и остановка. Именно поэтому базы и кластеры с кворумом живут в StatefulSet.

`Практика`

```bash
cd ~/lab/k8s
kubectl get storageclass
cat > sts.yaml <<'EOF'
apiVersion: v1
kind: Service
metadata: { name: pg }
spec:
  clusterIP: None            # headless: DNS отдаёт адреса подов, а не один VIP
  selector: { app: pg }
  ports: [{ port: 5432 }]
---
apiVersion: apps/v1
kind: StatefulSet
metadata: { name: pg }
spec:
  serviceName: pg
  replicas: 2
  selector: { matchLabels: { app: pg } }
  template:
    metadata: { labels: { app: pg } }
    spec:
      containers:
        - name: pg
          image: postgres:16-alpine
          env:
            - { name: POSTGRES_PASSWORD, value: labpass }
            - { name: PGDATA, value: /var/lib/postgresql/data/pgdata }
          ports: [{ containerPort: 5432 }]
          volumeMounts: [{ name: data, mountPath: /var/lib/postgresql/data }]
          readinessProbe:
            exec: { command: ["sh","-c","pg_isready -U postgres"] }
            periodSeconds: 5
  volumeClaimTemplates:
    - metadata: { name: data }
      spec:
        accessModes: [ReadWriteOnce]
        resources: { requests: { storage: 1Gi } }
EOF
kubectl apply -f sts.yaml
kubectl get pods -l app=pg -w --timeout=90s     # поднимаются по очереди: pg-0, потом pg-1
kubectl get pvc,pv

# стабильность имени и данных
kubectl exec pg-0 -- psql -U postgres -c 'create table t(x int); insert into t values (42);'
kubectl delete pod pg-0 && kubectl wait --for=condition=ready pod/pg-0 --timeout=90s
kubectl exec pg-0 -- psql -U postgres -c 'select * from t;'      # данные на месте
kubectl exec pg-1 -- psql -U postgres -c '\dt' 2>&1 | tail -2    # у второй реплики свой том — таблицы нет

# DNS у headless-сервиса
kubectl run dnstest --rm -it --image=busybox --restart=Never -- nslookup pg 2>/dev/null | tail -6

# что останется после удаления
kubectl delete statefulset pg
kubectl get pvc                                  # PVC не удаляются вместе со StatefulSet — это защита
kubectl delete pvc -l app=pg
```

`Проверка` Объясни, почему у каждой реплики StatefulSet свой PVC и что это значит для репликации (её настраивает не Kubernetes, а само приложение или оператор). Скажи, что произойдёт с данными при `kubectl delete statefulset`.

`Типичная ошибка` Запустить Postgres как Deployment с одним PVC и двумя репликами: два процесса на одном каталоге данных повреждают его. Второй вариант той же ошибки — `reclaimPolicy: Delete` на проде.

### 20. Helm: свой чарт и окружения

`Грейд` middle
`Время` 50 минут
`Вопросы` 87, 88, 89, 90, 91

`Зачем` Перестать копировать манифесты между dev, stage и prod.

**Теория.** Helm — шаблонизатор плюс менеджер релизов: он рендерит YAML из шаблонов и values, а результат хранит как релиз с номером ревизии, поэтому умеет `rollback`. Отличие от `kubectl apply` именно в этом: apply знает только текущее состояние объектов, Helm знает историю релизов целиком. Одно приложение — один чарт, окружения различаются только файлами values. Hooks позволяют выполнить работу до или после установки (миграция базы), но у них есть цена: неудачный hook блокирует релиз, а `helm rollback` не откатывает то, что hook уже сделал с данными.

`Практика`

```bash
cd ~/lab && helm create webapp && cd webapp
rm -rf templates/tests templates/hpa.yaml templates/ingress.yaml
ls templates/

# values по окружениям
cat > values-dev.yaml <<'EOF'
replicaCount: 1
image: { repository: traefik/whoami, tag: "v1.10" }
resources:
  requests: { cpu: 10m, memory: 16Mi }
  limits:   { cpu: 100m, memory: 64Mi }
EOF
cat > values-prod.yaml <<'EOF'
replicaCount: 4
image: { repository: traefik/whoami, tag: "v1.10" }
resources:
  requests: { cpu: 100m, memory: 128Mi }
  limits:   { cpu: 500m, memory: 256Mi }
EOF

# что получится — до установки в кластер
helm template webapp . -f values-prod.yaml | grep -E 'replicas|image:|cpu'
helm lint . -f values-prod.yaml
helm install webapp . -f values-dev.yaml --wait
helm list
kubectl get deploy webapp -o jsonpath='{.spec.replicas}'; echo

# апгрейд и откат по ревизиям
helm upgrade webapp . -f values-prod.yaml --wait
helm history webapp
kubectl get deploy webapp -o jsonpath='{.spec.replicas}'; echo
helm rollback webapp 1 --wait
kubectl get deploy webapp -o jsonpath='{.spec.replicas}'; echo

# отладка чарта, который не работает
helm upgrade webapp . --set replicaCount=НЕЧИСЛО 2>&1 | tail -3
helm template . --set image.tag="" --debug 2>&1 | tail -5
helm get manifest webapp | head -20
helm get values webapp

# hook: миграция перед апгрейдом
cat > templates/migrate.yaml <<'EOF'
apiVersion: batch/v1
kind: Job
metadata:
  name: {{ .Release.Name }}-migrate
  annotations:
    "helm.sh/hook": pre-upgrade
    "helm.sh/hook-weight": "-1"
    "helm.sh/hook-delete-policy": before-hook-creation,hook-succeeded
spec:
  template:
    spec:
      restartPolicy: Never
      containers:
        - name: migrate
          image: busybox
          command: ["sh","-c","echo применяю миграции; sleep 3"]
EOF
helm upgrade webapp . -f values-dev.yaml --wait
kubectl get jobs
helm uninstall webapp
```

`Проверка` Ты можешь объяснить разницу `helm upgrade` и `kubectl apply`, показать, как одно приложение едет в три окружения без копирования манифестов, и назвать опасность hooks при откате.

`Типичная ошибка` Отдельный чарт на каждое окружение. Через месяц они расходятся, и prod оказывается конфигурацией, которую никто не тестировал.

### 21. CI: от коммита до образа

`Грейд` middle
`Время` 55 минут
`Вопросы` 92, 93, 96, 98, 99, 160

`Зачем` Собрать пайплайн, который проверяет, собирает и публикует — и умеет запускаться локально.

**Теория.** Хороший пайплайн — это последовательность быстрых отказов: сначала линтеры и юнит-тесты (секунды), потом сборка образа, потом сканирование, и только потом деплой. Кэш ускоряет шаги и может быть невалидным; артефакт — результат сборки, который едет дальше по пайплайну и должен быть неизменяемым. Секреты в CI живут в переменных проекта или во внешнем хранилище, но никогда в коде; современный способ доступа к облаку — OIDC-токен на время выполнения задачи вместо долгоживущего ключа. Тег образа должен быть привязан к коммиту (`sha`), иначе нельзя понять, что запущено в проде.

`Практика`

```bash
cd ~/lab/thin
cat > .gitlab-ci.yml <<'EOF'
stages: [check, build, scan]

variables:
  IMAGE: $CI_REGISTRY_IMAGE:$CI_COMMIT_SHORT_SHA

lint:
  stage: check
  image: golangci/golangci-lint:latest
  script: [golangci-lint run ./... || true]

hadolint:
  stage: check
  image: hadolint/hadolint:latest-debian
  script: [hadolint Dockerfile]

build:
  stage: build
  image: gcr.io/kaniko-project/executor:debug
  script:
    - /kaniko/executor --context "$CI_PROJECT_DIR" --dockerfile Dockerfile
      --destination "$IMAGE" --destination "$CI_REGISTRY_IMAGE:latest"
  rules: [{ if: '$CI_COMMIT_BRANCH == "main"' }]

trivy:
  stage: scan
  image: aquasec/trivy:latest
  script: [trivy image --exit-code 1 --severity CRITICAL "$IMAGE"]
  allow_failure: true
EOF

# то же на GitHub Actions, чтобы запустить локально через act
mkdir -p .github/workflows
cat > .github/workflows/ci.yml <<'EOF'
name: ci
on: [push, workflow_dispatch]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Линтер Dockerfile
        uses: hadolint/hadolint-action@v3.1.0
        with: { dockerfile: Dockerfile }
      - name: Сборка
        run: docker build -t lab:${{ github.sha }} .
      - name: Проверка, что образ не от root
        run: test "$(docker inspect -f '{{.Config.User}}' lab:${{ github.sha }})" != ""
EOF

# локальный прогон без пуша — экономит десятки коммитов «fix ci»
act -l
act push --container-architecture linux/amd64 2>&1 | tail -20

# проверка синтаксиса GitLab CI локально
gitlab-ci-local --list 2>/dev/null || echo "поставь gitlab-ci-local для локального прогона"
```

Разбери, что не так с таким шагом, — это буквально задача с собеседования:

```yaml
deploy:
  script:
    - docker build -t myapp:latest .
    - docker push myapp:latest
    - kubectl set image deploy/app app=myapp:latest
```

Ответ: тег `latest` не даёт понять, что задеплоено, и откат невозможен; `kubectl set image` из CI — императивный деплой мимо git; пароль реестра, скорее всего, лежит в переменной без маскирования; нет ни тестов, ни сканирования; нет проверки, что rollout прошёл.

`Проверка` Ты можешь объяснить порядок стадий и зачем именно такой, разницу артефакта и кэша, когда нужен self-hosted runner (доступ во внутреннюю сеть,особое железо, лицензии) и почему тег по `sha` лучше `latest`.

`Типичная ошибка` Сборка образа в первом же шаге, до линтеров и тестов. Пайплайн честно тратит пять минут, чтобы потом упасть на опечатке в YAML.

### 22. GitOps: Argo CD, дрейф и самоисцеление

`Грейд` middle
`Время` 55 минут
`Вопросы` 95, 103, 225, 100

`Зачем` Понять разницу между «CI делает kubectl apply» и GitOps — это спрашивают сразу после Kubernetes.

**Теория.** В push-модели CI имеет доступ в кластер и применяет изменения; в pull-модели агент внутри кластера сам сравнивает желаемое состояние в git с фактическим и приводит их в соответствие. Отсюда три следствия: у CI больше нет прав в кластере (меньше поверхность атаки), git становится единственным источником правды и полным журналом изменений, а любое ручное изменение видно как дрейф и может быть автоматически отменено (self-heal). Откат превращается в `git revert`.

`Практика`

```bash
# установка Argo CD в лабораторный кластер
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
kubectl -n argocd rollout status deploy/argocd-server --timeout=180s
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath='{.data.password}' | base64 -d; echo
kubectl -n argocd port-forward svc/argocd-server 8443:443 >/dev/null 2>&1 &

# приложение из публичного репозитория с автосинхронизацией
cat > appofapps.yaml <<'EOF'
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: guestbook
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/argoproj/argocd-example-apps.git
    targetRevision: HEAD
    path: guestbook
  destination:
    server: https://kubernetes.default.svc
    namespace: guestbook
  syncPolicy:
    automated: { prune: true, selfHeal: true }
    syncOptions: [CreateNamespace=true]
EOF
kubectl apply -f appofapps.yaml
kubectl -n argocd get application guestbook -w --timeout=120s

# дрейф: меняем руками и смотрим, что будет
kubectl -n guestbook scale deploy guestbook-ui --replicas=5
kubectl -n guestbook get deploy guestbook-ui -o jsonpath='{.spec.replicas}'; echo
sleep 20
kubectl -n guestbook get deploy guestbook-ui -o jsonpath='{.spec.replicas}'; echo   # self-heal вернул как в git
kubectl -n argocd get application guestbook -o jsonpath='{.status.sync.status} {.status.health.status}'; echo

# удаление объекта тоже лечится
kubectl -n guestbook delete svc guestbook-ui
sleep 20 && kubectl -n guestbook get svc
```

Сравни на словах два способа деплоя одного и того же приложения и назови, что теряется в push-модели: журнал изменений (он остаётся в логах CI, а не в git), контроль дрейфа, и то, что права в кластер выданы наружу.

`Проверка` Ты можешь показать дрейф и самоисцеление на живом кластере и объяснить, почему GitOps — это про источник правды, а не про инструмент. Скажи, как в такой схеме делается откат.

`Типичная ошибка` Включить `selfHeal` и продолжать править кластер руками: изменения молча откатываются, и люди начинают считать, что «кластер глючит».

### 23. Terraform: state, модуль и дрейф

`Грейд` middle
`Время` 60 минут
`Вопросы` 101, 102, 104, 107, 108, 157

`Зачем` Работать с инфраструктурой в команде и не бояться слова state.

**Теория.** State — это карта соответствия между кодом и реальными объектами: без неё Terraform не знает, что `aws_instance.web` — это конкретный сервер, и предложит создать его заново. Отсюда два требования в команде: state лежит в общем удалённом бэкенде и блокируется на время операции, иначе два `apply` одновременно приведут к рассинхронизации. Ручное изменение в консоли создаёт дрейф: `plan` покажет разницу, и следующий `apply` вернёт как в коде. `count` даёт список (удаление элемента из середины пересоздаёт всё, что после него), `for_each` — карту по ключам (удаление затрагивает только один элемент). Версии провайдеров фиксируются, иначе сборка «вчера работала».

`Практика`

```bash
mkdir -p ~/lab/tf && cd ~/lab/tf
cat > main.tf <<'EOF'
terraform {
  required_version = ">= 1.6"
  required_providers {
    local  = { source = "hashicorp/local",  version = "~> 2.5" }
    random = { source = "hashicorp/random", version = "~> 3.6" }
  }
}

variable "envs" {
  type    = map(string)
  default = { dev = "1", stage = "2", prod = "4" }
}

resource "random_pet" "id" { length = 2 }

# for_each: ключи стабильны, удаление одного не трогает остальные
resource "local_file" "env" {
  for_each = var.envs
  filename = "${path.module}/out/${each.key}.conf"
  content  = "replicas=${each.value}\nid=${random_pet.id.id}\n"
}

output "files" { value = [for f in local_file.env : f.filename] }
EOF

terraform init
terraform fmt -check || terraform fmt
terraform validate
terraform plan -out=tfplan
terraform show -json tfplan | jq '.resource_changes[].change.actions' 2>/dev/null | sort | uniq -c
terraform apply tfplan
ls out/ && cat out/prod.conf

# state: что там внутри
terraform state list
terraform state show 'local_file.env["prod"]' | head -8

# дрейф: правим "руками" и смотрим plan
echo "replicas=99" > out/prod.conf
terraform plan | tail -20            # Terraform видит расхождение и хочет вернуть как в коде
terraform apply -auto-approve && cat out/prod.conf

# for_each против count: удалить stage
terraform apply -auto-approve -var 'envs={dev="1",prod="4"}'
ls out/                               # исчез только stage, dev и prod не пересоздавались

# полезные операции со state
terraform state mv 'local_file.env["dev"]' 'local_file.env["development"]' 2>/dev/null || true
terraform state list
terraform state rm 'random_pet.id' && terraform plan | head -12   # объект есть, в state его нет → хочет создать
terraform import random_pet.id "$(cat out/prod.conf | sed -n 's/^id=//p')" 2>/dev/null || terraform apply -auto-approve

# проверка кода до применения
terraform providers lock 2>/dev/null | tail -2
ls .terraform.lock.hcl                # именно он фиксирует версии в git
```

`Проверка` Объясни, что случится, если потерять state (Terraform перестанет знать о существующих объектах и предложит создать их заново; лечится импортом), зачем блокировка, и в чём разница `count` и `for_each` при удалении элемента из середины.

`Типичная ошибка` `terraform apply` без сохранённого плана в CI: между `plan` и `apply` состояние могло измениться, и применяется не то, что ревьюили. Правильно — `plan -out`, ревью, затем `apply tfplan`.

### 24. Ansible: идемпотентность и роли

`Грейд` middle
`Время` 50 минут
`Вопросы` 111, 112, 113, 114, 158

`Зачем` Писать плейбуки, которые можно запускать двадцать раз без последствий.

**Теория.** Идемпотентность — свойство операции давать одинаковый результат при повторе. В Ansible её обеспечивают модули: `apt`, `copy`, `lineinfile` сами проверяют текущее состояние и меняют только то, что отличается. Модуль `shell`/`command` идемпотентности не имеет — поэтому к нему нужны `creates`, `removes` или `changed_when`. Handlers выполняются один раз в конце, если что-то менялось, — так конфиг перечитывается только при реальном изменении. Для обновления парка серверов важны `serial` (партиями) и `max_fail_percentage` (остановиться, если падает слишком много).

`Практика`

```bash
mkdir -p ~/lab/ansible/roles/web/{tasks,handlers,templates,defaults} && cd ~/lab/ansible
printf 'localhost ansible_connection=local\n' > inventory

cat > roles/web/defaults/main.yml <<'EOF'
web_port: 8080
web_message: "привет из Ansible"
EOF
cat > roles/web/templates/site.conf.j2 <<'EOF'
# управляется Ansible, правки руками будут перезаписаны
listen {{ web_port }};
message "{{ web_message }}";
EOF
cat > roles/web/handlers/main.yml <<'EOF'
- name: перечитать конфиг
  ansible.builtin.debug: { msg: "reload выполнен, потому что конфиг изменился" }
EOF
cat > roles/web/tasks/main.yml <<'EOF'
- name: каталог конфигурации
  ansible.builtin.file:
    path: /tmp/labweb
    state: directory
    mode: "0755"

- name: конфиг из шаблона
  ansible.builtin.template:
    src: site.conf.j2
    dest: /tmp/labweb/site.conf
    mode: "0644"
  notify: перечитать конфиг

- name: строка в файле — идемпотентно
  ansible.builtin.lineinfile:
    path: /tmp/labweb/hosts
    line: "10.0.0.1 api.local"
    create: true
    mode: "0644"

# так делать нельзя: команда выполняется всегда
- name: плохой пример
  ansible.builtin.shell: "echo инициализация >> /tmp/labweb/init.log"
  changed_when: false          # хотя бы не врать в отчёте

# так правильно: команда один раз, дальше пропускается
- name: хороший пример
  ansible.builtin.shell: "echo инициализация > /tmp/labweb/init.marker"
  args: { creates: /tmp/labweb/init.marker }
EOF

cat > site.yml <<'EOF'
- hosts: all
  gather_facts: false
  serial: "50%"                # обновлять парк партиями
  max_fail_percentage: 20
  roles: [web]
EOF

ansible-playbook -i inventory site.yml            # первый прогон: changed
ansible-playbook -i inventory site.yml            # второй: ok, changed=0 — вот она, идемпотентность
ansible-playbook -i inventory site.yml --check --diff -e web_port=9090   # что изменится, ничего не меняя
ansible-playbook -i inventory site.yml -e web_port=9090   # handler сработал один раз

# секреты
ansible-vault create secrets.yml     # редактор откроется, впиши: db_password: s3cret
ansible-vault view secrets.yml
grep -c 'AES256' secrets.yml         # в git уезжает шифротекст, не пароль
```

`Проверка` Прогони плейбук дважды и покажи `changed=0` во втором прогоне. Объясни, почему `shell` без `creates` ломает идемпотентность и что делают `serial` и `max_fail_percentage` при обновлении сотни серверов.

`Типичная ошибка` Использовать `shell: systemctl restart nginx` вместо handler: сервис перезапускается на каждом прогоне, то есть плейбук вызывает микро-простой каждый раз, когда его запускают.

### 25. Prometheus и PromQL

`Грейд` middle
`Время` 60 минут
`Вопросы` 116, 117, 118, 154, 122

`Зачем` Писать запросы, а не тыкать в готовые дашборды: PromQL спрашивают почти на каждом собеседовании.

**Теория.** Prometheus работает по pull: сам опрашивает цели, поэтому знает, что цель недоступна (`up == 0`) — при push такая цель просто молчит, и это неотличимо от «всё хорошо». Типы метрик: counter только растёт (к нему всегда применяют `rate`), gauge — мгновенное значение, histogram — распределение по бакетам (из него считают квантили), summary — квантили, посчитанные на клиенте. Главное правило: **никогда не строить графики по счётчику напрямую**, только через `rate` или `increase`. Кардинальность — число уникальных комбинаций лейблов; лейбл с ID пользователя или URL с параметрами убивает Prometheus по памяти.

`Практика`

```bash
mkdir -p ~/lab/prom && cd ~/lab/prom
cat > prometheus.yml <<'EOF'
global: { scrape_interval: 5s }
scrape_configs:
  - job_name: prometheus
    static_configs: [{ targets: ["localhost:9090"] }]
  - job_name: node
    static_configs: [{ targets: ["node:9100"] }]
EOF
cat > compose.yaml <<'EOF'
services:
  prometheus:
    image: prom/prometheus:v3.1.0
    ports: ["9090:9090"]
    volumes: ["./prometheus.yml:/etc/prometheus/prometheus.yml:ro"]
  node:
    image: prom/node-exporter:v1.8.2
    pid: host
EOF
docker compose up -d && sleep 15

q() { curl -sG http://localhost:9090/api/v1/query --data-urlencode "query=$1" | jq -r '.data.result[0] | (.metric.instance // "-") + " → " + (.value[1] // "нет данных")'; }

# 1. живы ли цели — самый первый запрос на новом кластере
q 'up'
q 'count(up == 0)'

# 2. counter только через rate
q 'prometheus_http_requests_total'                    # бессмысленное растущее число
q 'sum(rate(prometheus_http_requests_total[1m]))'     # запросов в секунду — вот это имеет смысл

# 3. доля ошибок 5xx (то, что просят написать на собеседовании)
q 'sum(rate(prometheus_http_requests_total{code=~"5.."}[5m])) / sum(rate(prometheus_http_requests_total[5m]))'

# 4. квантиль задержки из histogram
q 'histogram_quantile(0.95, sum(rate(prometheus_http_request_duration_seconds_bucket[5m])) by (le))'

# 5. CPU узла: почему именно так
q '100 - (avg(rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)'

# 6. память и диск
q '(1 - node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes) * 100'
q 'predict_linear(node_filesystem_avail_bytes{mountpoint="/"}[6h], 4*24*3600) < 0'   # кончится ли диск за 4 дня

# 7. кардинальность: смотреть до того, как Prometheus упадёт
curl -s http://localhost:9090/api/v1/status/tsdb | jq '.data.seriesCountByMetricName[:5]'
q 'topk(3, count by (__name__)({__name__=~".+"}))'
```

`Проверка` Не подглядывая, напиши четыре запроса: доля 5xx за пять минут, 95-й перцентиль задержки, недоступные цели, рост занятого места на диске. Объясни, почему `rate` нужен counter и не нужен gauge.

`Типичная ошибка` Лейбл с высокой кардинальностью: `path="/api/user/12345"` вместо `path="/api/user/:id"`. Каждый уникальный путь — отдельный временной ряд; так Prometheus съедает память за сутки.

### 26. SLO, error budget и алерты без шума

`Грейд` middle
`Время` 50 минут
`Вопросы` 119, 120, 162, 126, 124

`Зачем` Говорить о надёжности числами. Это тот словарь, который превращает «дежурил на поддержке» в «владел надёжностью с измеримым SLO».

**Теория.** SLI — измеряемый показатель (доля успешных запросов, доля быстрых ответов). SLO — цель по этому показателю (99.9% успешных за 30 дней). SLA — внешнее обязательство с деньгами, и оно всегда слабее SLO, чтобы был запас. Error budget — допустимая доля ошибок: при 99.9% за 30 дней это 43 минуты 12 секунд недоступности. Бюджет — инструмент решений: пока он есть, катим релизы; кончился — останавливаем фичи и занимаемся надёжностью. Алертить надо на симптом, который видит пользователь (растёт доля ошибок, растёт задержка), а не на причину (загрузка CPU 90%), и делать это по скорости сжигания бюджета, а не по мгновенному значению.

`Практика`

```bash
cd ~/lab/prom
# посчитать бюджет руками — цифры надо знать наизусть
python3 - <<'EOF'
for slo in (99.0, 99.9, 99.95, 99.99):
    for days, label in ((30, "30 дней"), (1, "сутки")):
        m = (100 - slo) / 100 * days * 24 * 60
        print(f"SLO {slo}% за {label}: бюджет {m:.1f} мин")
EOF

# правила: SLI, запись и алерты на сжигание бюджета
cat > rules.yml <<'EOF'
groups:
  - name: slo
    interval: 15s
    rules:
      # SLI: доля успешных запросов
      - record: job:availability:ratio_rate5m
        expr: sum(rate(prometheus_http_requests_total{code!~"5.."}[5m]))
              / sum(rate(prometheus_http_requests_total[5m]))

      # быстрое сжигание: 14.4x за час → бюджет 30 дней сгорит за 2 дня
      - alert: ErrorBudgetBurnFast
        expr: (1 - job:availability:ratio_rate5m) > 14.4 * 0.001
        for: 2m
        labels: { severity: critical, page: "yes" }
        annotations:
          summary: "Быстрое сжигание бюджета ошибок"
          description: "Доля ошибок втрое выше допустимой. Бюджет 30 дней сгорит за двое суток."
          runbook: "https://nurekella.github.io/AboutMe/qa-trainer.html#q162"

      # медленное сжигание: не будит ночью, но создаёт задачу
      - alert: ErrorBudgetBurnSlow
        expr: (1 - job:availability:ratio_rate5m) > 3 * 0.001
        for: 1h
        labels: { severity: warning, page: "no" }
        annotations: { summary: "Медленное сжигание бюджета ошибок" }

      # симптом, а не причина: цель недоступна
      - alert: TargetDown
        expr: up == 0
        for: 2m
        labels: { severity: critical }
        annotations: { summary: "Цель {{ $labels.instance }} не отвечает" }
EOF
sed -i 's|^scrape_configs:|rule_files: ["/etc/prometheus/rules.yml"]\n\nscrape_configs:|' prometheus.yml
sed -i 's|- "./prometheus.yml:/etc/prometheus/prometheus.yml:ro"|- "./prometheus.yml:/etc/prometheus/prometheus.yml:ro"\n      - "./rules.yml:/etc/prometheus/rules.yml:ro"|' compose.yaml
docker compose up -d && sleep 20

curl -s 'http://localhost:9090/api/v1/rules' | jq -r '.data.groups[].rules[] | .name + " → " + (.type // "-")'
curl -sG http://localhost:9090/api/v1/query --data-urlencode 'query=job:availability:ratio_rate5m' | jq -r '.data.result[0].value[1]'
promtool check rules rules.yml 2>/dev/null || docker run --rm -v "$PWD:/w" prom/prometheus:v3.1.0 promtool check rules /w/rules.yml
```

`Проверка` Посчитай в уме бюджет для 99.9% за 30 дней и скажи, что делать, когда он кончился. Объясни, почему алерт «CPU выше 90%» плохой, а «доля 5xx выше порога десять минут» хороший.

`Типичная ошибка` Алерты на каждую метрику и всем в один канал. Через месяц их игнорируют, и настоящая авария проходит незамеченной. Правило: если на алерт не нужно реагировать ночью — он не должен будить, а если по нему нет действия — он не нужен.

---

## Грейд senior — масштаб и решения

Восемь уроков. Здесь спрашивают не команды, а решения: что делать, когда систем много, денег мало, а простой стоит дорого. Практика тоже другая — не «настрой», а «сломай, восстанови и посчитай».

### 27. Что происходит при kubectl apply

`Грейд` senior
`Время` 50 минут
`Вопросы` 59, 82, 86, 58

`Зачем` Отвечать на самый частый senior-вопрос по Kubernetes так, чтобы было видно понимание, а не заученный список.

**Теория.** Путь запроса: `kubectl` собирает манифест и отправляет его в kube-apiserver. Там последовательно происходит аутентификация (кто ты), авторизация через RBAC (можно ли тебе), затем admission-контроллеры: сначала mutating (могут менять объект — например, добавить sidecar или дефолтные значения), потом валидация схемы, потом validating (могут запретить — Kyverno, OPA). Только после этого объект пишется в etcd, и на этом `apply` заканчивается: **ответ «created» означает запись желаемого состояния, а не запущенное приложение**. Дальше асинхронно: deployment-controller видит новый объект и создаёт ReplicaSet, replicaset-controller создаёт поды, scheduler выбирает узлы и записывает `nodeName`, kubelet на узле видит «свой» под, просит CRI скачать образ и запустить контейнеры, CNI выдаёт адрес, kubelet шлёт статусы обратно. Всё это — контроллеры, крутящие один цикл: сравнить желаемое с фактическим, сделать шаг.

`Практика`

```bash
# 1. увидеть все стадии своими глазами
kubectl create deploy trace --image=traefik/whoami:v1.10 --replicas=2 -v=8 2>&1 | grep -E 'POST|Response Status' | head
kubectl get events --sort-by=.lastTimestamp | tail -12   # Scheduled → Pulling → Created → Started

# 2. что реально дописали admission-контроллеры
kubectl get pod -l app=trace -o yaml | grep -E 'serviceAccountName|imagePullPolicy|terminationGrace|dnsPolicy' | head
kubectl api-resources --namespaced=false | grep -i -E 'admission|policy'

# 3. кто принял решение о размещении
kubectl get pod -l app=trace -o custom-columns='POD:.metadata.name,NODE:.spec.nodeName,QOS:.status.qosClass'
kubectl get events --field-selector reason=Scheduled | tail -3

# 4. apply против create и replace
kubectl create deploy trace --image=nginx 2>&1 | tail -1        # AlreadyExists
kubectl apply -f - <<'EOF' 2>&1 | tail -2
apiVersion: apps/v1
kind: Deployment
metadata: { name: trace }
spec:
  replicas: 3
  selector: { matchLabels: { app: trace } }
  template:
    metadata: { labels: { app: trace } }
    spec: { containers: [{ name: whoami, image: traefik/whoami:v1.10 }] }
EOF
kubectl get deploy trace -o jsonpath='{.metadata.annotations}' | head -c 200; echo
# ↑ last-applied-configuration: именно по ней apply понимает, какие поля удалить

# 5. цикл контроллера: удалить ReplicaSet и посмотреть, кто его вернёт
kubectl delete rs -l app=trace --wait=false
sleep 5 && kubectl get rs -l app=trace
kubectl delete deploy trace
```

`Проверка` Расскажи путь вслух за две минуты, обязательно упомянув: apply возвращается до запуска приложения; между записью в etcd и работающим подом — цепочка независимых контроллеров; scheduler только записывает `nodeName`, запускает kubelet. Объясни, почему `kubectl apply` знает, какие поля удалять, а `create` — нет.

`Типичная ошибка` Рассказывать список компонентов («apiserver, etcd, scheduler, kubelet») вместо цепочки событий. Список знают все, ценность в понимании асинхронности и того, что каждый контроллер делает один шаг к желаемому состоянию.

### 28. etcd: кворум, бэкап и восстановление кластера

`Грейд` senior
`Время` 55 минут
`Вопросы` 79, 77, 78

`Зачем` Уметь ответить «а если etcd потеряли» не теорией, а описанием того, как ты это делал.

**Теория.** etcd — распределённое key-value хранилище на алгоритме Raft, единственный источник состояния кластера. Кворум — большинство узлов: из 3 переживает потерю 1, из 5 — потерю 2. Чётное число не даёт выигрыша: из 4 переживает тоже 1, но узлов больше и записи медленнее — поэтому 3 или 5. Потеря кворума означает, что кластер переходит в read-only: работающие приложения продолжают работать (kubelet и kube-proxy держат локальное состояние), но никакие изменения невозможны. Бэкапить нужно snapshot etcd плюс сертификаты PKI; манифесты приложений в бэкап кластера не входят, если у тебя GitOps, — они в git. Восстановление проверяется только репетицией.

`Практика`

```bash
# в k3d вместо etcd sqlite, поэтому берём отдельный контейнер etcd для практики
docker run -d --name etcd -p 2379:2379 \
  -e ALLOW_NONE_AUTHENTICATION=yes -e ETCD_ADVERTISE_CLIENT_URLS=http://0.0.0.0:2379 \
  bitnami/etcd:3.5
sleep 5
alias e='docker exec etcd etcdctl --endpoints=http://127.0.0.1:2379'

e put /registry/test "состояние кластера"
e get /registry/test
e endpoint status --write-out=table
e endpoint health
e member list --write-out=table

# снимок и что в нём
e snapshot save /tmp/snap.db
docker exec etcd etcdutl snapshot status /tmp/snap.db --write-out=table 2>/dev/null || \
  e snapshot status /tmp/snap.db --write-out=table
docker cp etcd:/tmp/snap.db ./etcd-snap.db && ls -lh etcd-snap.db

# катастрофа: потеряли данные
e del /registry/test
e get /registry/test                    # пусто

# восстановление из снимка
docker exec etcd sh -c 'etcdutl snapshot restore /tmp/snap.db --data-dir=/tmp/restored' 2>/dev/null || \
  docker exec etcd sh -c 'ETCDCTL_API=3 etcdctl snapshot restore /tmp/snap.db --data-dir=/tmp/restored'
docker exec etcd ls /tmp/restored/member/snap | head -3
echo "дальше в проде: остановить etcd на всех узлах, подложить восстановленный data-dir, поднять по одному"

# в реальном кластере команда выглядит так (kubeadm)
cat <<'EOF'
ETCDCTL_API=3 etcdctl \
  --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key \
  snapshot save /backup/etcd-$(date +%F-%H%M).db
EOF

# что ещё нужно в бэкапе кластера, кроме etcd
cat <<'EOF'
1. snapshot etcd (состояние всех объектов)
2. /etc/kubernetes/pki — без сертификатов кластер не поднять
3. PV с данными приложений — отдельно, инструментом вроде Velero
4. манифесты — в git, если GitOps; иначе тоже в бэкап
EOF
docker rm -f etcd
```

`Проверка` Объясни, почему узлов 3 или 5, что происходит с работающими приложениями при потере кворума, и назови четыре части бэкапа кластера. Скажи вслух, что бэкап без проверенного восстановления бэкапом не является.

`Типичная ошибка` Считать, что snapshot etcd достаточно для восстановления. Без PKI кластер не поднимется, а без бэкапа PV приложения поднимутся пустыми.

### 29. Отладка сети между подами

`Грейд` senior
`Время` 50 минут
`Вопросы` 81, 64, 159, 33

`Зачем` Это самая частая живая задача на техническом интервью: «поды не видят друг друга, разберись».

**Теория.** Порядок проверки идёт снизу вверх и на каждом шаге даёт однозначный ответ: DNS резолвится? адрес пода пингуется? порт открыт? приложение слушает на нужном интерфейсе (`0.0.0.0`, а не `127.0.0.1`)? есть ли endpoints у Service? не режет ли NetworkPolicy? Половина случаев — не сеть: приложение слушает только localhost, или селектор Service не совпал с метками, или readiness не проходит и адрес не попал в endpoints.

`Практика`

```bash
kubectl create ns netlab 2>/dev/null
kubectl -n netlab run server --image=python:3.12-slim --labels=app=server \
  -- python3 -m http.server 8000 --bind 127.0.0.1      # намеренная ошибка: только localhost
kubectl -n netlab expose pod server --port 8000
kubectl -n netlab run client --image=nicolaka/netshoot --labels=app=client -- sleep 3600
kubectl -n netlab wait --for=condition=ready pod/client --timeout=60s

# шаг 1: DNS
kubectl -n netlab exec client -- dig +short server.netlab.svc.cluster.local
# шаг 2: адрес пода
IP=$(kubectl -n netlab get pod server -o jsonpath='{.status.podIP}')
kubectl -n netlab exec client -- ping -c1 -W2 $IP
# шаг 3: порт
kubectl -n netlab exec client -- nc -zv -w2 $IP 8000 ; echo "результат: $?"
# шаг 4: где слушает приложение — вот причина
kubectl -n netlab exec server -- sh -c 'apt-get -qq update >/dev/null 2>&1; apt-get -qq install -y iproute2 >/dev/null 2>&1; ss -tlnp' 2>/dev/null | tail -3
# шаг 5: endpoints
kubectl -n netlab get endpoints server

# починить: слушать на всех интерфейсах
kubectl -n netlab delete pod server --wait=true
kubectl -n netlab run server --image=python:3.12-slim --labels=app=server -- python3 -m http.server 8000 --bind 0.0.0.0
kubectl -n netlab expose pod server --port 8000 2>/dev/null
kubectl -n netlab wait --for=condition=ready pod/server --timeout=60s
kubectl -n netlab exec client -- curl -s -m3 -o /dev/null -w 'код %{http_code}\n' http://server:8000

# вторая причина: селектор не совпал
kubectl -n netlab patch svc server -p '{"spec":{"selector":{"app":"НЕВЕРНО"}}}'
kubectl -n netlab get endpoints server
kubectl -n netlab exec client -- curl -s -m3 http://server:8000 ; echo "код: $?"
kubectl -n netlab patch svc server -p '{"spec":{"selector":{"app":"server"}}}'

# третья: политика режет трафик
kubectl -n netlab apply -f - <<'EOF'
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata: { name: deny-all }
spec: { podSelector: {}, policyTypes: [Ingress] }
EOF
kubectl -n netlab exec client -- curl -s -m3 http://server:8000 ; echo "с политикой код: $?"
kubectl -n netlab get networkpolicy
kubectl -n netlab delete networkpolicy deny-all

# смотреть трафик внутри пода
kubectl -n netlab exec client -- sh -c 'timeout 5 tcpdump -ni any port 8000 -c 3 & sleep 1; curl -s -m3 http://server:8000 >/dev/null; wait' 2>/dev/null | tail -5
kubectl delete ns netlab --wait=false
```

`Проверка` Проговори шесть проверок по порядку и назови три причины, которые выглядят как сетевая проблема, но ею не являются: приложение слушает localhost, селектор Service не совпал, readiness не проходит.

`Типичная ошибка` Начинать с NetworkPolicy и CNI. В девяти случаях из десяти дело в метках, готовности или интерфейсе прослушивания — и это проверяется тремя командами.

### 30. Disaster recovery: RTO, RPO и репетиция

`Грейд` senior
`Время` 55 минут
`Вопросы` 226, 128, 238, 77

`Зачем` Отвечать на «а если ЦОД сгорит» числами и планом, а не «у нас есть бэкапы».

**Теория.** RTO — сколько времени допустимо восстанавливаться. RPO — сколько данных допустимо потерять. Это бизнес-решения, а не технические: их называет владелец сервиса, а инженер говорит, сколько стоит каждый вариант. RPO задаёт схему репликации: RPO в часах — периодические бэкапы, в минутах — WAL-архив и PITR, близкий к нулю — синхронная репликация со своей ценой в задержке записи. RTO задаёт схему резерва: холодный (восстановление из бэкапа, часы), тёплый (реплика, которую надо повысить, минуты), горячий (активный резерв, секунды). Главное: **план восстановления, который не репетировали, не работает** — по опыту первая репетиция всегда обнаруживает отсутствующие сертификаты, забытые DNS-записи и бэкапы, которые не читаются.

`Практика`

```bash
mkdir -p ~/lab/dr && cd ~/lab/dr
# 1. база с данными и настоящий PITR
docker run -d --name pg -e POSTGRES_PASSWORD=labpass -p 5433:5432 postgres:16
sleep 8
docker exec pg psql -U postgres -c 'create table payments(id serial, amount int, created timestamptz default now());'
docker exec pg psql -U postgres -c 'insert into payments(amount) select generate_series(1,1000);'
docker exec pg psql -U postgres -c 'select count(*), max(created) from payments;'

# 2. бэкап с замером времени — RPO и RTO измеряются, а не оцениваются
time docker exec pg pg_dump -U postgres -Fc postgres > dump.pgc
ls -lh dump.pgc

# 3. авария: потеряли данные после бэкапа
docker exec pg psql -U postgres -c 'insert into payments(amount) values (99999);'
docker exec pg psql -U postgres -c 'drop table payments;'

# 4. восстановление с замером — это и есть твой RTO
START=$(date +%s)
docker exec -i pg pg_restore -U postgres -d postgres --clean --if-exists < dump.pgc 2>/dev/null
docker exec pg psql -U postgres -c 'select count(*) from payments;'
END=$(date +%s); echo "RTO этого сценария: $((END-START)) секунд"
echo "RPO: всё, что записано после снимка — строка 99999 потеряна навсегда"

# 5. посчитать, что обещать бизнесу
python3 - <<'EOF'
plans = [
    ("бэкап раз в сутки",        24*60, 60,  "дёшево, теряем до суток данных"),
    ("бэкап + WAL-архив (PITR)",     5, 45,  "потеря минуты, восстановление под час"),
    ("тёплая реплика",               1, 10,  "промоут реплики, нужен второй сервер"),
    ("синхронная реплика",           0,  2,  "нулевая потеря, платим задержкой записи"),
]
print(f"{'схема':<28}{'RPO':>8}{'RTO':>8}  примечание")
for name, rpo, rto, note in plans:
    print(f"{name:<28}{rpo:>6} мин{rto:>6} мин  {note}")
EOF

# 6. чеклист репетиции — то, что отличает план от разговоров
cat > runbook.md <<'EOF'
# Репетиция восстановления, раз в квартал
1. Поднять чистое окружение (не прод!)
2. Восстановить последний бэкап, зафиксировать реальное время → это RTO
3. Проверить целостность: количество строк, последняя транзакция, контрольные запросы
4. Проверить, что есть сертификаты и секреты для запуска приложений
5. Переключить DNS/балансировщик на резерв, замерить время распространения
6. Записать, что не сработало, и исправить до следующей репетиции
EOF
docker rm -f pg
```

`Проверка` Назови свои RTO и RPO для учебного сценария в секундах — измеренные, а не предположенные. Объясни разницу RTO и RPO на примере и скажи, почему нельзя обещать RPO=0 без синхронной репликации.

`Типичная ошибка` Отвечать «у нас настроены бэкапы Veeam». Правильный ответ включает числа, схему и дату последней успешной репетиции восстановления.

### 31. Мультитенантность: один кластер на несколько команд

`Грейд` senior
`Время` 50 минут
`Вопросы` 228, 80, 72, 73

`Зачем` Это типовая senior-задача: дать десяти командам общий кластер так, чтобы они не мешали друг другу.

**Теория.** Namespace изолирует **имена и права**, но не изолирует сеть (по умолчанию любой под ходит куда угодно), не изолирует узлы (соседняя команда может занять весь CPU) и не даёт квоты по умолчанию. Поэтому мультитенантность собирается из слоёв: namespace + RBAC (кто), ResourceQuota и LimitRange (сколько), NetworkPolicy default deny (с кем говорить), политики Kyverno или OPA (что запрещено — root, hostPath, `latest`), и при жёстких требованиях — отдельные узлы через taints или вообще отдельный кластер. Ключевой вопрос на собеседовании: где граница между «жёсткая изоляция в одном кластере» и «дешевле дать отдельный кластер» — ответ обычно в требованиях регулятора и в том, нужен ли командам собственный набор CRD и версий.

`Практика`

```bash
kubectl create ns team-a 2>/dev/null; kubectl create ns team-b 2>/dev/null
kubectl label ns team-a team=a --overwrite; kubectl label ns team-b team=b --overwrite

# 1. квоты: сколько команда может взять
kubectl apply -f - <<'EOF'
apiVersion: v1
kind: ResourceQuota
metadata: { name: quota, namespace: team-a }
spec:
  hard:
    requests.cpu: "1"
    requests.memory: 1Gi
    limits.cpu: "2"
    limits.memory: 2Gi
    pods: "10"
    persistentvolumeclaims: "3"
    services.loadbalancers: "0"      # чтобы не выставляли сервисы в интернет сами
---
apiVersion: v1
kind: LimitRange
metadata: { name: defaults, namespace: team-a }
spec:
  limits:
    - type: Container
      default:        { cpu: 100m, memory: 128Mi }   # если забыли указать limits
      defaultRequest: { cpu: 50m,  memory: 64Mi }
      max:            { cpu: "1",  memory: 1Gi }
EOF

# LimitRange дописывает ресурсы за того, кто их не указал
kubectl -n team-a run nolimits --image=traefik/whoami:v1.10
sleep 3
kubectl -n team-a get pod nolimits -o jsonpath='{.spec.containers[0].resources}'; echo

# квота реально останавливает
kubectl -n team-a create deploy greedy --image=nginx --replicas=1
kubectl -n team-a patch deploy greedy --type=json -p='[{"op":"add","path":"/spec/template/spec/containers/0/resources","value":{"requests":{"cpu":"900m","memory":"900Mi"}}}]'
kubectl -n team-a scale deploy greedy --replicas=3
sleep 5
kubectl -n team-a get events --field-selector reason=FailedCreate | tail -2   # exceeded quota
kubectl -n team-a describe quota quota | tail -12

# 2. сеть: команды не видят друг друга
kubectl apply -f - <<'EOF'
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata: { name: isolate, namespace: team-a }
spec:
  podSelector: {}
  policyTypes: [Ingress]
  ingress:
    - from: [{ namespaceSelector: { matchLabels: { team: a } } }]
EOF

# 3. права: команда видит только свой namespace
kubectl create serviceaccount dev-a -n team-a 2>/dev/null
kubectl create rolebinding dev-a-edit --clusterrole=edit --serviceaccount=team-a:dev-a -n team-a
kubectl auth can-i get pods -n team-a --as=system:serviceaccount:team-a:dev-a
kubectl auth can-i get pods -n team-b --as=system:serviceaccount:team-a:dev-a
kubectl auth can-i get nodes --as=system:serviceaccount:team-a:dev-a

# 4. узлы только для команды — когда нужна изоляция по железу
NODE=$(kubectl get nodes -o name | tail -1 | cut -d/ -f2)
kubectl taint node $NODE tenant=team-a:NoSchedule --overwrite
kubectl label node $NODE tenant=team-a --overwrite
echo "теперь поды team-a с toleration поедут только сюда, чужие — не поедут вообще"
kubectl taint node $NODE tenant=team-a:NoSchedule-

kubectl delete ns team-a team-b --wait=false
```

`Проверка` Назови по памяти четыре слоя изоляции и что именно каждый закрывает. Ответь на вопрос «namespace изолирует?» правильно: имена и права — да, сеть, ресурсы и узлы — нет, пока не настроишь.

`Типичная ошибка` Считать namespace изоляцией. Без квот одна команда съедает кластер, без политик ходит в чужие сервисы, без LimitRange запускает поды без лимитов, и первый же OOM на узле убивает чужие поды.

### 32. Наблюдаемость на масштабе

`Грейд` senior
`Время` 50 минут
`Вопросы` 239, 122, 125, 121

`Зачем` Отвечать на «как построить мониторинг для сорока сервисов» так, чтобы это не превратилось в сорок дашбордов и счёт на десятки тысяч.

**Теория.** Один сервис мониторят как хотят; сорок — только по единому контракту. Контракт: каждый сервис отдаёт одни и те же четыре сигнала (частота запросов, доля ошибок, задержка, насыщенность) с одинаковыми именами метрик и одинаковым набором лейблов, дашборд один и параметризуется переменной сервиса, алерты генерируются из шаблона, а не пишутся руками. Три источника данных не заменяют друг друга: метрики отвечают «что-то не так и насколько», логи — «что именно случилось в этом запросе», трейсы — «в каком из десяти сервисов задержка». Стоимость растёт не от числа сервисов, а от кардинальности и от сроков хранения — поэтому сэмплирование трейсов, ограничение лейблов и разные сроки для сырых и агрегированных данных.

`Практика`

```bash
cd ~/lab/prom
# 1. найти, что съедает хранилище — первое, что делают на масштабе
curl -s http://localhost:9090/api/v1/status/tsdb | jq '{
  ряды: .data.headStats.numSeries,
  топ_метрик: (.data.seriesCountByMetricName[:5] | map({(.name): .value}) | add),
  топ_лейблов: (.data.labelValueCountByLabelName[:5] | map({(.name): .value}) | add)
}'

# 2. посчитать кардинальность и цену конкретного лейбла
curl -sG http://localhost:9090/api/v1/query --data-urlencode \
  'query=topk(5, count by (__name__)({__name__=~".+"}))' | jq -r '.data.result[] | .metric.__name__ + " → " + .value[1]'
python3 - <<'EOF'
# грубая, но полезная оценка: сколько стоит один лейбл с высокой кардинальностью
bytes_per_sample = 2          # после сжатия
scrape = 15                   # секунд
for series in (10_000, 100_000, 1_000_000):
    per_day = series * (86400/scrape) * bytes_per_sample / 1e9
    print(f"{series:>9} рядов → {per_day:6.1f} ГБ/сутки → {per_day*30:7.0f} ГБ за месяц")
EOF

# 3. единый контракт: правила генерируются из шаблона, а не пишутся руками
cat > gen-rules.py <<'PY'
services = ["api", "billing", "search", "auth"]
tpl = """      - alert: {svc}HighErrorRate
        expr: |
          sum(rate(http_requests_total{{service="{svc}",code=~"5.."}}[5m]))
          / sum(rate(http_requests_total{{service="{svc}"}}[5m])) > 0.01
        for: 10m
        labels: {{ severity: critical, service: {svc} }}
        annotations: {{ summary: "{svc}: доля 5xx выше 1%" }}
"""
print("groups:\n  - name: generated\n    rules:")
for s in services:
    print(tpl.format(svc=s), end="")
PY
python3 gen-rules.py > generated-rules.yml && head -12 generated-rules.yml
docker run --rm -v "$PWD:/w" prom/prometheus:v3.1.0 promtool check rules /w/generated-rules.yml

# 4. сроки хранения: сырое коротко, агрегаты долго
cat <<'EOF'
Recording rule агрегирует до дешёвого ряда:
  record: service:http_errors:ratio_rate5m
  expr:   sum by (service) (rate(http_requests_total{code=~"5.."}[5m]))
          / sum by (service) (rate(http_requests_total[5m]))
Сырые метрики держим 15 дней, агрегаты — год. Отчёт за прошлый квартал строится
по агрегатам и стоит копейки.
EOF

# 5. сколько стоит хранение логов против метрик — аргумент в разговоре о бюджете
python3 - <<'EOF'
rps, days = 2000, 30
log_bytes = 400
raw = rps * 86400 * days * log_bytes / 1e12
print(f"логи: {rps} rps × {days} дней × {log_bytes} Б = {raw:.2f} ТБ")
print(f"метрики того же сервиса при 200 рядах: {200*(86400/15)*2*days/1e9:.2f} ГБ")
print("вывод: логи сэмплировать и хранить коротко, агрегаты и метрики — долго")
EOF
```

`Проверка` Объясни, зачем нужны все три источника данных и что именно теряется, если оставить только логи. Назови два способа снизить стоимость наблюдаемости, не теряя диагностическую ценность (агрегаты плюс короткое хранение сырых, сэмплирование трейсов с сохранением всех ошибочных).

`Типичная ошибка` Строить отдельный дашборд под каждый сервис. Через год их сто, половина сломана, и никто не знает, какой из них правильный.

### 33. Деньги: стоимость сервиса и обоснование надёжности

`Грейд` senior
`Время` 45 минут
`Вопросы` 224, 136, 247, 219

`Зачем` Senior отличается от middle умением говорить с бизнесом в его единицах. Это же напрямую влияет на твою вилку.

**Теория.** Стоимость сервиса складывается из инфраструктуры (вычисления, память, диск, трафик), лицензий, и того, что обычно забывают: времени людей на эксплуатацию. В Kubernetes инфраструктурную часть считают через долю requests пода в ресурсах узла, плюс общие сервисы (мониторинг, логи, ingress) распределяются по потребителям. Главный источник экономии — не скидки у провайдера, а разница между requests и фактическим потреблением: если запрошено вдвое больше, чем используется, половина счёта — воздух. Разговор о надёжности переводится в деньги так: стоимость минуты простоя × ожидаемое время простоя за год против стоимости резерва. Если резерв дороже ожидаемых потерь, его не надо делать — и это тоже правильный инженерный ответ.

`Практика`

```bash
# 1. сколько запрошено против того, сколько используется
kubectl get pods -A -o custom-columns='NS:.metadata.namespace,POD:.metadata.name,CPU_REQ:.spec.containers[*].resources.requests.cpu,MEM_REQ:.spec.containers[*].resources.requests.memory' | head -15
kubectl top pods -A 2>/dev/null | head -10 || echo "нужен metrics-server: kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml"
kubectl describe nodes | grep -A5 'Allocated resources' | head -20

# 2. посчитать стоимость сервиса
python3 - <<'EOF'
node_month_usd = 120          # цена узла в месяц
node_cpu, node_mem = 8, 32    # ядер и ГБ

services = [
    # имя,      реплик, requests CPU, requests ГБ, фактическое потребление CPU
    ("api",         6, 0.5, 1.0, 0.12),
    ("billing",     3, 1.0, 2.0, 0.30),
    ("search",      4, 0.5, 4.0, 0.45),
]
cpu_price = node_month_usd / 2 / node_cpu      # половину цены узла относим на CPU
mem_price = node_month_usd / 2 / node_mem      # половину на память

print(f"{'сервис':<10}{'запрошено':>12}{'использует':>12}{'переплата':>12}")
total = waste = 0
for name, rep, cpu, mem, used in services:
    booked = rep * (cpu*cpu_price + mem*mem_price)
    real   = rep * (used*cpu_price + mem*mem_price)
    total += booked; waste += booked - real
    print(f"{name:<10}{booked:>10.0f} $ {real:>10.0f} $ {booked-real:>10.0f} $")
print(f"\nвсего в месяц: {total:.0f} $, из них воздух: {waste:.0f} $ ({waste/total*100:.0f}%)")
print(f"плюс общие сервисы (мониторинг, ingress, логи) — обычно 15-25% сверху")
EOF

# 3. обосновать резерв: считаем ожидаемые потери против цены
python3 - <<'EOF'
revenue_per_min = 3000        # выручка в минуту в рабочее время
current_slo, target_slo = 99.5, 99.95
minutes_year = 365*24*60
for slo in (current_slo, target_slo):
    down = (100-slo)/100 * minutes_year
    print(f"SLO {slo}%: простой {down:.0f} мин/год, потери {down*revenue_per_min/1e6:.2f} млн")
saved = ((100-current_slo)-(100-target_slo))/100 * minutes_year * revenue_per_min
print(f"\nэкономия от перехода: {saved/1e6:.2f} млн в год")
print("стоимость: второй ЦОД + синхронная репликация ≈ 0.9 млн в год")
print("вывод для бизнеса: вложение окупается втрое — это и есть обоснование")
EOF

# 4. быстрые источники экономии, которые видно за час
kubectl get pvc -A --no-headers 2>/dev/null | wc -l    # сколько дисков, все ли нужны
kubectl get pv --no-headers 2>/dev/null | awk '$5=="Released"' | wc -l   # брошенные тома, за которые платят
kubectl get svc -A --field-selector spec.type=LoadBalancer --no-headers 2>/dev/null | wc -l   # каждый LB — отдельный счёт
```

`Проверка` Посчитай на своих числах, сколько стоит один сервис в месяц, и назови три источника экономии, которые не требуют переписывания приложения (привести requests к фактическому потреблению, убрать брошенные тома и лишние LoadBalancer, разные сроки хранения телеметрии). Сформулируй одним предложением, почему надёжность стоит своих денег в твоём случае.

`Типичная ошибка` Обосновывать надёжность словами «это best practice». Бизнес слышит «инженер хочет игрушку». Единица разговора — деньги: стоимость минуты простоя, ожидаемое число минут, цена резерва.

### 34. Chaos engineering и процесс инцидентов

`Грейд` senior
`Время` 60 минут
`Вопросы` 236, 243, 165, 124, 229

`Зачем` Проверить, что система и процесс выдерживают отказ, до того как это проверит прод. И потренировать первые пять минут аварии вслух.

**Теория.** Chaos engineering — не «сломать прод», а эксперимент с гипотезой: формулируем ожидание («при потере одного пода доля ошибок не превысит 0.1%»), задаём радиус поражения, включаем наблюдение, ломаем, сравниваем с гипотезой, откатываем. Начинают в тестовом окружении и с самого дешёвого сценария — убийства пода. Процесс инцидентов на масштабе — про роли, а не про героизм: incident commander координирует и сам не чинит, communications lead общается с бизнесом, остальные работают по гипотезам, кто-то ведёт таймлайн. Постмортем blameless и отвечает не на «что сломалось», а на «что позволило этому дойти до прода и какой проверки не хватало».

`Практика`

```bash
cd ~/lab/k8s
# подопытный сервис с честной readiness и антиаффинити
kubectl apply -f - <<'EOF'
apiVersion: apps/v1
kind: Deployment
metadata: { name: chaos-app }
spec:
  replicas: 4
  selector: { matchLabels: { app: chaos-app } }
  template:
    metadata: { labels: { app: chaos-app } }
    spec:
      topologySpreadConstraints:
        - maxSkew: 1
          topologyKey: kubernetes.io/hostname
          whenUnsatisfiable: ScheduleAnyway
          labelSelector: { matchLabels: { app: chaos-app } }
      containers:
        - name: app
          image: traefik/whoami:v1.10
          readinessProbe: { httpGet: { path: /, port: 80 }, periodSeconds: 2 }
---
apiVersion: v1
kind: Service
metadata: { name: chaos-app }
spec:
  selector: { app: chaos-app }
  ports: [{ port: 80 }]
EOF
kubectl rollout status deploy/chaos-app

# эксперимент 1: гипотеза — потеря одного пода не даёт ошибок клиенту
kubectl run load --image=curlimages/curl:8.10.1 -- sh -c '
  ok=0; err=0
  for i in $(seq 1 200); do
    if curl -s -m 2 -o /dev/null http://chaos-app; then ok=$((ok+1)); else err=$((err+1)); fi
    sleep 0.2
  done
  echo "успешных: $ok, ошибок: $err"' >/dev/null
sleep 5
kubectl delete pod -l app=chaos-app --field-selector=status.phase=Running --wait=false 2>/dev/null | head -1
sleep 45 && kubectl logs load

# эксперимент 2: гипотеза — потеря узла восстанавливается автоматически
kubectl get pods -l app=chaos-app -o wide
NODE=$(kubectl get pods -l app=chaos-app -o jsonpath='{.items[0].spec.nodeName}')
kubectl drain $NODE --ignore-daemonsets --delete-emptydir-data --force --timeout=90s
kubectl get pods -l app=chaos-app -o wide          # переехали на живые узлы
kubectl uncordon $NODE

# эксперимент 3: гипотеза — зависимость отвечает медленно, а не падает
kubectl run slow --image=nicolaka/netshoot --rm -it --restart=Never -- \
  sh -c 'tc qdisc add dev eth0 root netem delay 300ms 2>/dev/null; time curl -s -o /dev/null http://chaos-app; exit' 2>/dev/null

kubectl delete pod load --ignore-not-found; kubectl delete deploy chaos-app; kubectl delete svc chaos-app
```

Теперь тренировка речи. Возьми таймер на две минуты и расскажи вслух первые пять минут аварии: подтвердить и объявить (не молчать), оценить масштаб по симптомам, вспомнить что менялось за последний час, локализовать по границам, действовать по одной гипотезе с фиксацией таймлайна. Затем запиши постмортем по шаблону:

```bash
cat > ~/lab/postmortem.md <<'EOF'
# Постмортем: <короткое описание>

**Влияние.** Что видел пользователь, сколько времени, сколько запросов и денег.
**Обнаружение.** Как узнали: мониторинг или клиент? Если клиент — это пункт №1 в выводах.
**Таймлайн.** Время → что увидели → что сделали → эффект.
**Первопричина.** Техническая причина и то, что позволило ей дойти до прода.
**Что сработало.** Не только плохое: что помогло быстро восстановиться.
**Action items.** Каждый пункт убирает класс проблемы, а не конкретный случай.
  Владелец и срок обязательны, иначе это не пункт, а пожелание.
EOF
cat ~/lab/postmortem.md
```

`Проверка` У тебя есть три проведённых эксперимента с записанными гипотезами и результатами, и ты можешь рассказать первые пять минут аварии за две минуты, не задумываясь. Объясни, почему incident commander не чинит руками.

`Типичная ошибка` Начинать хаос-эксперименты с прода и без наблюдения: тогда это не эксперимент, а авария, устроенная своими руками. И постмортем, в котором первопричина — «человеческая ошибка»: это означает, что настоящую причину — отсутствие проверки, которая эту ошибку бы поймала, — не нашли.
