# Бот @myregibot — добавление клиента по Telegram

По сообщению в Telegram бот добавляет клиента в раздел **Клиенты** (contract_maker). Работает прямо из Django.

---

## Что нужно

- В `.env` заданы **TELEGRAM_BOT_TOKEN** и **TELEGRAM_CHAT_ID** (тот же chat_id, что для уведомлений о регистрации).
- **TELEGRAM_CHAT_ID** — твой Telegram chat id. Бот **отвечает только тебе**: сообщения из других чатов игнорируются (защита от чужих запросов и спама).
- Бот должен быть запущен на том же компе/сервере, где крутится проект (доступ к той же БД).

---

## Запуск

В одном терминале — сайт (если ещё не запущен):

```bash
python manage.py runserver
```

Во **втором** терминале — бот:

```bash
python manage.py run_myregibot
```

Оставь оба окна открытыми. В консоли бота появится:  
`Бот @myregibot запущен. Ожидаю сообщения (добавь клиента …). Ctrl+C — выход.`

---

## Как пользоваться

Напиши боту в Telegram (тому, у которого токен в TELEGRAM_BOT_TOKEN, например @myregibot) **одним из вариантов**:

- **Добавь клиента ООО Ромашка**
- **Создай клиента ИП Петров**
- **Зарегистрируй компанию ЗАО Вектор**
- **Add customer Test LLC**

После названия/ФИО можно писать что угодно — в базу попадёт строка после фразы «клиента» / «компанию» / «customer».  
Бот ответит, например:  
`Клиент «ООО Ромашка» добавлен в базу (id=5).`

Проверить: на сайте **Договоры → создать договор** (или список клиентов) — новый клиент должен появиться в списке.

---

## Остановка

В терминале, где запущен `run_myregibot`, нажми **Ctrl+C**.

---

## Запуск на автомате

### Вариант 1: Docker

При запуске проекта бот уже поднимается вместе с сайтом:

```bash
docker compose up -d
```

Сервис `bot` в `docker-compose.yml` запускается автоматически и перезапускается при падении. При перезагрузке сервера после `docker compose up -d` бот снова будет работать.

---

### Вариант 2: Linux-сервер (systemd)

Чтобы бот стартовал при загрузке сервера и перезапускался при сбоях:

1. Создай unit-файл (пример в репозитории: **contract_maker/myregibot.service.example**).
2. Скопируй его в systemd и подставь свои пути и пользователя:
   ```bash
   sudo cp contract_maker/myregibot.service.example /etc/systemd/system/myregibot.service
   sudo nano /etc/systemd/system/myregibot.service
   ```
   В файле укажи:
   - **WorkingDirectory** — каталог с `manage.py`;
   - **EnvironmentFile** — путь к `.env`;
   - **ExecStart** — полный путь к `python` из venv и `manage.py run_myregibot`;
   - **User** / **Group** — пользователь, под которым крутится Django (например `www-data`).
3. Включи и запусти:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable myregibot
   sudo systemctl start myregibot
   ```
4. Проверка: `sudo systemctl status myregibot`, логи: `sudo journalctl -u myregibot -f`.

После обновления кода: `sudo systemctl restart myregibot`.

---

### Вариант 3: Windows (локально)

- **Планировщик заданий**: создай задачу «При запуске компьютера» или «При входе в систему», действием укажи запуск `cmd` или `powershell` с командой вида  
  `C:\path\to\venv\Scripts\python.exe C:\path\to\manage.py run_myregibot`  
  (рабочая папка — каталог с `manage.py`).
- Либо положи в автозагрузку ярлык/батник, который открывает консоль и запускает эту команду (бот будет в отдельном окне).
