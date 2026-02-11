# Запуск проекта в Docker

## Подготовка

1. **Файл `.env`**  
   В каталоге с `docker-compose.yml` должен быть файл `.env` (скопируй из `example.env` и заполни):
   - `SECRET_KEY`, `ALLOWED_HOSTS`, `DEBUG`
   - для уведомлений в Telegram и бота: `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`
   - при необходимости: Cloudinary, БД, `CONTRACT_MAKER_BOT_TOKEN` и т.д.

2. **Миграции**  
   При первом запуске выполни миграции (один раз):
   ```bash
   docker compose run --rm web python manage.py migrate
   ```
   Создай суперпользователя при необходимости:
   ```bash
   docker compose run --rm web python manage.py createsuperuser
   ```

## Запуск

```bash
docker compose up -d
```

Поднимаются сервисы:
- **redis** — для Channels/чат
- **web** — Django (Daphne), порт 8001 → 8000
- **bot** — бот @myregibot (добавление клиента по Telegram)
- **nginx** — порт 8080 → 80

Сайт доступен на порту **8080** (через nginx) или **8001** (напрямую к web).

## Бот в Docker

Сервис **bot** запускается вместе с **web** и использует:
- тот же образ и тот же код;
- ту же БД (общий volume `.:/app`, при SQLite — один и тот же `db.sqlite3`);
- переменные из того же `.env` (`TELEGRAM_BOT_TOKEN` и др.).

Бот работает в фоне: long polling к Telegram, по фразам «добавь клиента …» создаёт клиента в contract_maker. Остановка бота: `docker compose stop bot`. Запуск только бота: `docker compose up -d bot`.

## Полезные команды

```bash
# Логи (все сервисы)
docker compose logs -f

# Логи только бота
docker compose logs -f bot

# Остановить всё
docker compose down

# Пересобрать образы после изменения кода/зависимостей
docker compose build --no-cache
docker compose up -d
```

## Статика

При монтировании тома `.:/app` каталог `staticfiles` в контейнере перекрывается именованным томом. Если статика не подхватывается, один раз выполни:
```bash
docker compose run --rm web python manage.py collectstatic --noinput
```
