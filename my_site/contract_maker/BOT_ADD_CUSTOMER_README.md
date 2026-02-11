# Тест бота: добавление клиента через API

## 1. Что уже есть в Django

- **URL:** `POST /contract-maker/api/customer/add/`  
  Полный адрес при запуске на своём компе:  
  **`http://127.0.0.1:8000/contract-maker/api/customer/add/`**

- **Токен:** в `.env` задаётся переменная `CONTRACT_MAKER_BOT_TOKEN=твой_секрет`.  
  Если она **задана** — бот обязан передавать этот же токен.  
  Если **не задана** — запросы принимаются без проверки (удобно для теста локально).

- **Тело запроса (JSON):**
  - обязательно: **`org_name`** — название организации или ФИО физлица;
  - по желанию: `client_type` (`"legal"` или `"individual"`), `rep_position`, `rep_name`, `basis`, `short_name`, `address`, `unp`, `okpo`, `iban`;
  - если используешь токен: **`token`** в теле или заголовок **`X-Bot-Token`**.

- **Ответ:**  
  Успех: `{"ok": true, "id": 5, "org_name": "ООО Рога"}`  
  Ошибка: `{"ok": false, "error": "текст"}`

---

## 2. Быстрый тест с командной строки (без бота)

Сервер должен быть запущен (`python manage.py runserver`).

**Без токена (если в .env нет CONTRACT_MAKER_BOT_TOKEN):**
```bash
curl -X POST http://127.0.0.1:8000/contract-maker/api/customer/add/ ^
  -H "Content-Type: application/json" ^
  -d "{\"org_name\": \"Тест из curl ООО Рога\"}"
```
(В PowerShell кавычки экранируй по необходимости или используй один символ ` вместо ^.)

**С токеном в теле:**
```bash
curl -X POST http://127.0.0.1:8000/contract-maker/api/customer/add/ ^
  -H "Content-Type: application/json" ^
  -d "{\"org_name\": \"Тест из curl\", \"token\": \"ТВОЙ_ТОКЕН_ИЗ_ENV\"}"
```

**Или тестовый скрипт (из папки с manage.py):**
```bash
set CONTRACT_MAKER_BOT_TOKEN=твой_токен
python -m contract_maker.test_bot_add_customer
```

После успешного запроса в разделе «Клиенты» в админке или в списке клиентов при создании договора появится новый клиент.

---

## 3. Бот @myregibot (добавление клиента по сообщению в Telegram)

См. файл **[MYREGIBOT_README.md](MYREGIBOT_README.md)** — запуск команды `python manage.py run_myregibot`: бот слушает Telegram и по фразам «добавь клиента …» создаёт клиента в базе.
