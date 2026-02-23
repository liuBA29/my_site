# Архитектура Telegram-бота (my_site)

Бот и всё, что с ним связано, живёт в приложении **`bot`** — конструктор для текущего бота и будущих ботов/ИИ-ассистентов. Уведомления с сайта по-прежнему вызывают отправку через общую утилиту (для совместимости импорт остаётся из `accounts`).

## Общая схема

Один бот в Telegram (один токен `TELEGRAM_BOT_TOKEN`, один аккаунт, например @myregibot), два способа использования:

```
                    ┌─────────────────────────────────────────────────────────┐
                    │              Telegram Bot (один токен)                  │
                    └─────────────────────────────────────────────────────────┘
                                          ▲
                    ┌─────────────────────┼─────────────────────┐
                    │                     │                     │
           «Руль 1»: уведомления   «Руль 2»: интерактивный бот   Опционально: внешний
           (сайт → Telegram)       (Telegram → бот → ответ)       клиент по HTTP API
                    │                     │                     │
                    │                     │                     │
              Django (сайт)         run_myregibot           api_add_customer
              send_telegram()       getUpdates +             POST …/api/customer/add/
                                   send_telegram(chat_id)   (добавить клиента)
```

---

## Где что лежит (приложение `bot`)

| Компонент | Путь | Назначение |
|-----------|------|------------|
| Отправка в Telegram | `bot/telegram.py` → `send_telegram(text, chat_id=None)` | Базовый конструктор: одна функция для уведомлений и ответов бота. При сбое исключения не пробрасываются. |
| Действие «добавить клиента» | `bot/actions/add_customer.py` → `add_customer_from_payload(data)` | Общая логика для Telegram-команды и HTTP API: создаёт/находит `Customer` в БД (модель в contract_maker). |
| HTTP API | `bot/views.py` → `api_add_customer` | POST JSON, проверка CONTRACT_MAKER_BOT_TOKEN, вызов `add_customer_from_payload`, ответ JSON. |
| Интерактивный бот | `bot/management/commands/run_myregibot.py` | Long polling getUpdates, разбор «добавь клиента …», вызов `add_customer_from_payload`, ответ через `send_telegram(..., chat_id=chat_id)`. |

Обратная совместимость: `accounts/telegram_utils.py` реэкспортирует `send_telegram` из `bot.telegram`; `accounts/views.py` по-прежнему определяет `send_telegram_message(text)` и импортирует из `bot.telegram`. URL добавления клиента не менялся: в `contract_maker/urls.py` маршрут `api/customer/add/` ведёт на `bot.views.api_add_customer`.

---

## 1. Единая точка отправки в Telegram

**Файл:** `bot/telegram.py` (реэкспорт для старого кода: `accounts/telegram_utils.py` → `bot.telegram`)

- **Функция:** `send_telegram(text, chat_id=None)`
- **Поведение:**
  - Если `chat_id` не передан — используется `TELEGRAM_CHAT_ID` (уведомления с сайта).
  - Если передан — отправка в указанный чат (ответы бота пользователю).
- **Надёжность:** при любой ошибке (бот недоступен, неверный токен, сеть, таймаут) исключения не пробрасываются, в лог пишется предупреждение, сайт продолжает работать.

Все исходящие сообщения в Telegram идут только через эту функцию.

---

## 2. Руль 1: уведомления с сайта (сайт → Telegram)

Сайт (Django) в определённых событиях шлёт сообщение **в один и тот же чат** — `TELEGRAM_CHAT_ID` (группа или личка).

**Обёртка для удобства:** `accounts/views.py` → `send_telegram_message(text)` вызывает `send_telegram(text)` из `bot.telegram`.

| Событие | Где вызывается | Что уходит в Telegram |
|--------|----------------|------------------------|
| Регистрация пользователя | `accounts/views.py` (register_view) | «Новый пользователь зарегистрировался: …» |
| Вход в админку (успешный) | `accounts/signals.py` (user_logged_in) | Сообщение с пользователем, email, IP, время |
| Неудачная попытка входа в админку | `accounts/signals.py` (user_login_failed) | Предупреждение с username, IP, путём, временем |
| Новая заявка (форма на сайте) | `main_app/views.py` (order/contact) | Заявка: имя, email, телефон, продукт, описание, IP |
| Пользователь зашёл в чат | `chat/consumers.py` (WebSocket connect) | «User … has joined the chat!» (если не superuser) |

Все эти вызовы не блокируют ответ пользователю: при сбое Telegram только не приходит уведомление, страница/чат работают как обычно.

---

## 3. Руль 2: интерактивный бот (Telegram → бот → ответ)

**Команда:** `python manage.py run_myregibot`  
**Файл:** `bot/management/commands/run_myregibot.py`

Отдельный долгоживущий процесс:

1. **Long polling** — периодически запрашивает `getUpdates` у Telegram (новые сообщения в боте).
2. **Фильтр по чатам** — обрабатывает только сообщения из разрешённых `chat_id` (переменные `TELEGRAM_BOT_ALLOWED_CHAT_ID` или `TELEGRAM_BOT_ALLOWED_CHAT_IDS`, иначе fallback на `TELEGRAM_CHAT_ID`).
3. **Распознавание команд** — по шаблонам вроде «добавь клиента …», «создай клиента …» извлекается название организации.
4. **Действие** — вызывается `bot.actions.add_customer_from_payload({"org_name": ...})` (создаётся или находится `Customer` в БД contract_maker).
5. **Ответ** — в тот же чат отправляется сообщение через `send_telegram(reply, chat_id=chat_id)`.

Если пользователь пишет что-то вроде «добавь договор» — бот отвечает подсказкой, что пока умеет только добавлять клиентов (сайт liuba.site, раздел Договоры).

Бот и сайт используют одну и ту же БД: клиенты, добавленные через бота, видны в разделе «Договоры» на сайте.

---

## 4. HTTP API для добавления клиента

**Endpoint:** `POST …/contract-maker/api/customer/add/` (подключён в `contract_maker/urls.py`, view — `bot.views.api_add_customer`)

- Для работы **обязателен** `CONTRACT_MAKER_BOT_TOKEN` в настройках. Если не задан — всегда 403.
- В запросе нужен токен: заголовок `X-Bot-Token` или поле `token` в JSON.
- Тело: JSON с полями клиента (`org_name`, `client_type`, `rep_name` и т.д.). Логика создания — общая с ботом: `bot.actions.add_customer_from_payload(data)`.

Внешний скрипт или другой сервис может добавлять клиентов без запуска run_myregibot (например, другой бот или автоматизация). Тест: `contract_maker/test_bot_add_customer.py`.

---

## 5. Настройки (переменные окружения / .env)

| Переменная | Назначение |
|------------|------------|
| `TELEGRAM_BOT_TOKEN` | Токен бота от @BotFather. Общий для уведомлений и для run_myregibot. |
| `TELEGRAM_CHAT_ID` | Куда слать уведомления с сайта (регистрация, заявки, админка, чат). |
| `TELEGRAM_BOT_ALLOWED_CHAT_ID` | Один разрешённый chat_id для команд боту (например, твой user id в личке). |
| `TELEGRAM_BOT_ALLOWED_CHAT_IDS` | Несколько chat_id через запятую (если бот должен отвечать нескольким пользователям). |
| `CONTRACT_MAKER_BOT_TOKEN` | Токен для HTTP API добавления клиента; если не задан — API возвращает 403. |

Если не заданы `TELEGRAM_BOT_ALLOWED_*`, run_myregibot использует `TELEGRAM_CHAT_ID` как список разрешённых чатов.

---

## 6. Зависимости между компонентами

```
bot/telegram.py (send_telegram)
    ▲
    ├── accounts/views.py (send_telegram_message → send_telegram)
    │       ▲
    │       ├── accounts/signals.py
    │       ├── main_app/views.py
    │       └── chat/consumers.py (через sync_to_async)
    │
    └── bot/management/commands/run_myregibot.py (send_telegram с chat_id)

bot/actions/add_customer.py (add_customer_from_payload)
    ▲
    ├── bot/views.py (api_add_customer)
    └── bot/management/commands/run_myregibot.py

contract_maker: модель Customer, маршрут api/customer/add/ → bot.views.api_add_customer
accounts/telegram_utils.py: реэкспорт send_telegram из bot.telegram (обратная совместимость)
```

---

## 7. Кратко

- **Один бот** — один токен, один аккаунт в Telegram.
- **Всё про бота в приложении `bot`** — telegram.py, actions/, views, management/commands. Конструктор для текущего и будущих ботов/ИИ-ассистентов.
- **Два «руля»:** (1) сайт шлёт уведомления в `TELEGRAM_CHAT_ID`; (2) run_myregibot принимает сообщения, через `add_customer_from_payload` добавляет клиентов, отвечает в чат отправителя.
- **Одна функция отправки** — `send_telegram` в `bot/telegram.py`; при сбоях Telegram сайт не падает.
- **Общая логика «добавить клиента»** — `add_customer_from_payload` в `bot/actions/add_customer.py`; используется и в run_myregibot, и в HTTP API.
- **Обратная совместимость** — старый импорт из `accounts.telegram_utils` и `accounts.views.send_telegram_message` сохранён; URL API не менялся.
