# Lab 03: власний DevOps-інструментарій

**Основні завдання: 8 балів; бонуси: до 6 балів.** Проєкт містить три обов'язкові інструменти та три бонуси. Для Bash-скриптів потрібен Linux/macOS/WSL/Git Bash (моніторинг системи лише Linux), для Python — 3.9+, для Go-бонусу — Go 1.20+. Жодних Python-бібліотек, окрім стандартної бібліотеки, не потрібно.

## Структура

- `backup.sh` — архівація й ротація резервних копій
- `api_monitor.py` — перевірки HTTP(S), категорії помилок, повторний запит, JSON-звіт, Discord-сповіщення
- `config/endpoints.json` — конфігурація API-монітора
- `hooks/pre-commit` та `hooks/pre-push` — Git-хуки
- `install-hooks.sh` — інсталятор хуків
- `monitor.sh`, `config/system.env` — бонус: стан машини
- `log_analyzer.py`, `samples/access.log` — бонус: аналіз combined access log
- `file_sorter.go`, `go.mod`, `file_sorter_test.go` — бонус: сортувальник файлів на Go
- `tests/` — тести

## 1. Резервне копіювання

```bash
chmod +x backup.sh
./backup.sh --help
./backup.sh --source "./samples" --dest "/tmp/lab03-backups" --keep 3
./backup.sh --source "./samples" --dest "/tmp/lab03-backups" --keep 3 --dry-run
```

`set -euo pipefail` означає: `-e` завершує скрипт на необробленій помилці; `-u` вважає використання незаданої змінної помилкою; `pipefail` робить помилку будь-якої команди в конвеєрі помилкою всього конвеєра. Без них скрипт міг би мовчки продовжити роботу після невдалої архівації, використати порожній шлях або приховати збій у конвеєрі.

Скрипт перевіряє параметри, створює `.tar.gz` із назвою джерела й UTC-міткою часу, зберігає останні N архівів **лише цього джерела** в теці призначення (через хеш абсолютного шляху), журналює події у `backup.log`, показує розмір архіву. `--dry-run` нічого не створює й не видаляє, лише показує дії. Шляхи з пробілами підтримуються. Помилки: `2` параметри, `3` шлях/доступ, `4` архівація. Задля безпеки джерело не може містити теку призначення.

## 2. API-монітор

```bash
python3 api_monitor.py --help
python3 api_monitor.py --config config/endpoints.json --output monitor-results.json
export MONITOR_WEBHOOK_URL='https://discord.com/api/webhooks/ВАШ_ID/ВАШ_ТОКЕН'
python3 api_monitor.py --config config/endpoints.json --output monitor-results.json
```

Формат конфігурації JSON:

```json
{"targets": [{"name":"Demo","url":"https://example.com/","expected_status":200,"timeout":5,"slow_threshold":2}]}
```

Типи збою: `dns` (домен не розпізнано); `connection_refused` (TCP-підключення відхилено); `timeout` (не отримано відповідь до тайм-ауту); `certificate_error` (TLS-сертифікат не прийнято); `unexpected_status` (HTTP-код не збігається з очікуваним); `slow_response` (правильний код, але надто повільно); `network_error` (інші мережеві проблеми). При мережевому збої робиться **одна** повторна спроба. Усі результати, включно з тривалістю, кодом і типом збою, записуються у JSON. Для кожної проблемної цілі надсилається повідомлення через Discord webhook, якщо задана змінна середовища. Без webhook локальний запис працює, але сповіщення не надсилаються. Вихід: `0` усі здорові, `1` є проблеми, `2` некоректна конфігурація, `3` не вдалося зберегти звіт.

**Як демонструвати чотири типи збоїв:** `nonexistent-devops-lab-03.invalid` демонструє DNS, `127.0.0.1:1` за відсутності локального слухача демонструє відмову підключення, `expired.badssl.com` демонструє помилку сертифіката, `/not-found-devops-lab-03` демонструє неочікуваний код. Реальні відповіді залежать від мережі, проксі й доступності тестових вузлів: перевіряйте отриманий `monitor-results.json`. Для реального інциденту **відмова підключення** означає, що хост доступний, але конкретний порт не приймає з'єднання (перевірити процес, порт, firewall); **тайм-аут** означає, що відповіді вчасно немає (перевірити мережу, маршрутизацію, перевантаження або зависання застосунку).

## 3. Git-хуки

```bash
chmod +x install-hooks.sh
./install-hooks.sh
```

Перед комітом `pre-commit` запускає `shellcheck` для **лише staged** `.sh`, а також `py_compile` і `ruff check` для **лише staged** `.py` файлів. Якщо є проблеми, коміт блокується. `pre-push` запускає `python3 -m unittest discover -s lab-03/tests -v`, відхиляючи push у разі помилок. Додатково можна запустити `bash lab-03/tests/test_backup.sh`, `go test ./...` з теки `lab-03`.

Хуки знаходяться в `.git/hooks` локального клону, Git **не версіонує їх автоматично**. Тому вони збережені у `hooks/` та встановлюються копіюванням через `install-hooks.sh`. **Хуки не є засобом примусового контролю:** розробник може їх обійти через `git -c core.hooksPath=/dev/null ...` або `--no-verify` для відповідних команд. Обов'язкові серверні перевірки налаштовуються у CI та захисті гілок, де учасник не може просто обійти правила локально.

## Бонус 1: моніторинг Linux

```bash
chmod +x monitor.sh
./monitor.sh --config config/system.env
# */5 * * * * /absolute/path/lab-03/monitor.sh --config /absolute/path/lab-03/config/system.env
```

Вимірює CPU через дві вибірки `/proc/stat`, RAM через `MemAvailable`, диск через `df`, процеси/сервіси через `systemctl` (список `SERVICES` у конфігурації). Пороги задаються в `config/system.env`, жоден не захардкоджений у логіці. При перевищенні порогу друкується `ALERT`, робиться запис у журнал, код виходу `1`; інакше `OK`, код `0`. Для демонстрації задайте `CPU_MAX=0` або `DISK_MAX=0` та запустіть на Linux. Конфігурацію `system.env` треба вважати довіреним shell-файлом.

## Бонус 2: аналіз журналів веб-сервера

```bash
python3 log_analyzer.py --input samples/access.log --output reports/access-report.txt --format text --top 5
python3 log_analyzer.py --input samples/access.log --output reports/access-report.json --format json --top 3
```

Парсить Apache/Nginx **combined** формат: IP, дату, HTTP-код. Виводить топ-N IP, кількість статусів за класами (2xx, 3xx тощо), пікові години (зведені запити по кожній годині). Некоректні рядки не валять скрипт, підраховуються окремо. Тест перевіряє парсинг валідного та невалідного рядка.

## Бонус 3: Go-утиліта

```bash
mkdir -p /tmp/lab03-sort
printf 'demo' > /tmp/lab03-sort/test.pdf
go run file_sorter.go -dir /tmp/lab03-sort -dry-run
go build -o file-sorter file_sorter.go
./file-sorter -dir /tmp/lab03-sort
go test ./...
```

Підкоманди/прапорці: `-dir`, `-dry-run`, `-h`. Групує файли верхнього рівня на `documents`, `images`, `videos`, `archives`, `other`. Не перезаписує наявні файли. Статичний бінарник для Linux: `CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -o file-sorter file_sorter.go` (збирати на системі з Go). **Порівняння:** Go-бінарник зазвичай більший за кількакілобайтний shell/Python-скрипт, але не вимагає окремого встановленого інтерпретатора на цільовій машині; час запуску Go також часто кращий для невеликих утиліт. Bash зручний для швидких задач з UNIX-командами; Go корисний для переносимих програм, структурованих помилок і складнішої логіки. Розміри й час залежать від ОС, інструментарію й обладнання, тож для кількісного порівняння виміряйте `ls -lh file-sorter` та `time ./file-sorter -dir /tmp/lab03-sort -dry-run`, і порівняйте зі скриптом.

## Тестування

```bash
python3 -m unittest discover -s tests -v
bash tests/test_backup.sh
go test ./...
```

## Здача через Pull Request

1. Скопіюйте **теку `lab-03/`** у корінь свого репозиторію `devops-portfolio` (не завантажуйте весь архів як один файл).
2. `git checkout -b lab-03-tools`
3. `git add lab-03 && git commit -m "Add DevOps tools lab 03"`
4. `git push -u origin lab-03-tools`
5. На GitHub відкрийте Pull Request із `lab-03-tools` у `main`. Не робіть прямий push у `main`.
6. На захисті продемонструйте запуск, режими помилок, тести та поясніть прийняті рішення.

**Примітка:** приклади тестових доменів можуть поводитися по-різному залежно від мережі; URL та пороги можна змінити в `config/endpoints.json`. Webhook-токен ніколи не комітьте.
