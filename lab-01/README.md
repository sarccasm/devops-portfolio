# Lab 01 — Git and development environment

## Мета

Підготувати робоче середовище і репозиторій так, щоб усі наступні роботи курсу виконувались у цьому репозиторії, а зміни в `main` проходили через pull request.

---

## 1. Git і редактор

### Глобальні параметри Git

Використані налаштування:

```bash
git config --global user.name "Artem Fivko"
git config --global user.email "a.fivko@gmail.com"
git config --global init.defaultBranch main
git config --global pull.rebase true
git config --global core.editor "code --wait"
```

Для Windows:

```bash
git config --global core.autocrlf true
```

Для macOS/Linux:

```bash
git config --global core.autocrlf input
```

Перевірка:

```bash
git config --list --global
```

### Чому `core.autocrlf` різний у Windows та Unix

Windows традиційно використовує завершення рядків `CRLF`, а Linux/macOS — `LF`. На Windows `core.autocrlf=true` дає змогу Git перетворювати `LF` на `CRLF` при checkout і повертати рядки до `LF` під час commit. На Unix-подібних системах `core.autocrlf=input` не змінює `LF` у робочій директорії, але нормалізує випадкові `CRLF` до `LF` під час commit. Це зменшує кількість беззмістовних diff через різні системи завершення рядків.

### Чим `pull.rebase=true` відрізняється від merge

Звичайний `git pull` може виконати merge віддаленої та локальної історії й створити додатковий merge commit. При `pull.rebase=true` локальні коміти тимчасово прибираються, віддалені зміни застосовуються першими, після чого локальні коміти переносяться поверх них. У результаті історія зазвичай лишається лінійною та легшою для читання.

### Вивід `git config --list --global`

> Після виконання команд на робочій машині вставити фактичний вивід тут або додати скріншот у `assets/`.

```text
user.name=Artem Fivko
user.email=a.fivko@gmail.com
init.defaultbranch=main
pull.rebase=true
core.editor=code --wait
core.autocrlf=true
```

### Редактор

Для роботи використовується VS Code. Потрібні можливості:

- Git history / author blame — GitLens або вбудовані Git-функції;
- Docker / Compose — Docker extension;
- YAML validation — YAML extension від Red Hat;
- Markdown preview — вбудований preview або Markdown All in One.

Файл `.editorconfig` у корені задає пробіли, `LF`, UTF-8 та фінальний перенос рядка. VS Code має застосовувати ці правила при збереженні.

### Перевірка YAML

Для перевірки підсвічування помилки тимчасово створюється YAML із неправильним відступом, наприклад:

```yaml
name: Test

jobs:
  build:
   runs-on: ubuntu-latest
    steps:
      - run: echo "test"
```

Скріншот редактора з підсвіченою помилкою зберігається як:

```text
lab-01/assets/yaml-validation.png
```

Після скріншота навмисно зламаний YAML не додається до репозиторію.

---

## 2. Середовище виконання

### Node.js

Node.js встановлюється через version manager (`nvm` / `nvm-windows`), а не системним пакетом. Поточна LTS-гілка та ще одна підтримувана версія використовуються для демонстрації перемикання на одній машині.

Приклад:

```bash
nvm install 22
nvm install 24
nvm use 22
node --version
nvm use 24
node --version
```

Скріншот перемикання між двома версіями:

```text
lab-01/assets/node-version-switch.png
```

### Python

Python встановлюється через менеджер версій або `uv`, а не покладається лише на системну інсталяцію.

Приклад з `uv`:

```bash
uv python install 3.14
uv python list
```

### Контейнеризація

Для лабораторних використовується Docker Desktop. Перевірка:

```bash
docker --version
docker compose version
```

Використовується саме Compose v2 через команду `docker compose`, а не застарілий окремий executable `docker-compose`.

### Навіщо менеджер версій, коли проєктів більше одного

Різні проєкти можуть мати різні вимоги до Node.js або Python. Менеджер версій дозволяє встановити кілька версій паралельно й перемикатися між ними без перевстановлення всієї системи. Це робить середовище відтворюванішим і зменшує ризик, що оновлення одного проєкту зламає інший.

---

## 3. GitHub і доступ

### GitHub account

Профіль має заповнене ім'я, фото та короткий опис. Для акаунта ввімкнена двофакторна автентифікація.

### SSH

Створення ключа:

```bash
ssh-keygen -t ed25519 -C "a.fivko@gmail.com"
```

За умовою лабораторної passphrase лишається порожньою. У GitHub додається лише публічна частина `id_ed25519.pub`.

Перевірка:

```bash
ssh -T git@github.com
```

Очікуваний результат містить успішну автентифікацію GitHub для користувача `sarccasm`.

Скріншот перевірки:

```text
lab-01/assets/ssh-github.png
```

### Чому приватний SSH-ключ не можна додавати до репозиторію

Приватний ключ підтверджує особу власника. Якщо він опиниться у публічному репозиторії, стороння людина зможе скопіювати його й потенційно автентифікуватися від імені власника. Тому приватна частина ключа має зберігатися лише локально та ніколи не комітитися.

### Що робити, якщо приватний ключ усе ж потрапив у репозиторій

1. Вважати ключ скомпрометованим і негайно припинити його використання.
2. Видалити відповідний public key у GitHub Settings → SSH and GPG keys.
3. Згенерувати нову пару ключів.
4. Додати новий public key до GitHub і перевірити доступ.
5. Прибрати секрет з усієї історії Git, а не лише з останнього commit, якщо репозиторій уже був опублікований.
6. Повідомити команду, якщо ключ міг надати доступ до спільних ресурсів, і перевірити журнали доступу за потреби.

---

## 4. Портфоліо-репозиторій

Створено публічний репозиторій:

```text
https://github.com/sarccasm/devops-portfolio
```

### README

Кореневий `README.md` містить коротке представлення, професійну мету в DevOps, знайомі технології, план навчання на рік, структуру репозиторію та контакти.

### `.gitignore`

`.gitignore` не писався як випадковий список вручну: він сформований на основі gitignore.io / Toptal-style шаблонів для таких категорій:

- Node
- Python
- Visual Studio Code
- Windows
- macOS
- Linux

### Ліцензія

Обрана **MIT License**. Для навчального публічного портфоліо вона підходить тому, що дозволяє іншим переглядати, використовувати, змінювати й поширювати код за умови збереження copyright та license notice, не накладаючи складних додаткових обмежень.

### Структура

У репозиторії підготовлено `lab-01` … `lab-10` і `final`. Папки майбутніх робіт містять лише `.gitkeep`, оскільки Git не відстежує порожні директорії.

---

## 5. Правила репозиторію

Для гілки `main` налаштовується ruleset:

- pull request обов'язковий перед merge;
- force-push заборонений;
- видалення `main` заборонене;
- історія має бути лінійною.

На цій лабораторній **не вмикаються** required status checks, mandatory approvals і повна заборона bypass для адміністратора, оскільки CI ще не запускався і репозиторій персональний.

### Що зміниться, коли робота стане командною

У командному репозиторії правила треба посилити: додати щонайменше один approval, за потреби CODEOWNERS review, обов'язкове проходження CI status checks, resolution обговорень та чітку політику merge. Так зміна не потрапить до `main` без незалежної перевірки та автоматичних тестів.

### Чому зараз небезпечно повністю забороняти обхід правил адміністратором

У персональному репозиторії одна людина є і автором, і власником. Якщо помилково зробити обов'язковим approval іншої людини або required check, якого ще не існує, можна заблокувати merge власних змін. У команді bypass теж має бути максимально обмеженим, але потрібна контрольована аварійна процедура на випадок зламаної CI-конфігурації чи іншої критичної ситуації.

### GitHub Project

Project board має колонки:

```text
Backlog → In Progress → Review → Done
```

Автоматизації:

- нова задача → `Backlog`;
- відкритий PR → `Review`;
- merged PR → `Done`;
- закрита задача → `Done`.

Створюється окрема задача для кожної лабораторної та фінального проєкту.

### Pull request template

Файл `.github/pull_request_template.md` містить:

- опис змін;
- посилання на задачу;
- список змін;
- self-check checklist;
- спосіб перевірки результату.

---

## Перевірка структури

```text
devops-portfolio/
├── README.md
├── .gitignore
├── LICENSE
├── .editorconfig
├── .github/
│   └── pull_request_template.md
├── lab-01/
│   ├── README.md
│   └── assets/
├── lab-02/
├── lab-03/
├── lab-04/
├── lab-05/
├── lab-06/
├── lab-07/
├── lab-08/
├── lab-09/
├── lab-10/
└── final/
```

## Файли доказів у `lab-01/assets/`

Після виконання команд на моїй машині додаються реальні скріншоти:

```text
yaml-validation.png
node-version-switch.png
ssh-github.png
```

За потреби також можна додати:

```text
git-config.png
docker-compose.png
github-ruleset.png
github-project.png
```
