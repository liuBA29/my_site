<!--
Short, targeted instructions for AI coding agents working on this repo.
Focus on concrete, discoverable patterns (Django + Channels + Cloudinary + contract_maker) and developer workflows.
-->

# Copilot / AI coding instructions for this repository

Be concise. Prefer edits that preserve existing project layout and conventions. This project is a Django site (Django 5.x) using ASGI/Channels (Daphne), Redis channel layers, Cloudinary for media, and a small contract generator. Key app directories: `main_app`, `chat`, `accounts`, `contract_maker`, `notes_app`.

Key points an AI should know before proposing changes
- The repository root for runtime is `my_site/` (contains `manage.py`, `my_site/settings.py`).
- Environment is driven by a `.env` file and keys are read with `python-dotenv` in `settings.py` and `contract_maker/generator_config.py`.
- ASGI and WebSockets: `ASGI_APPLICATION` is configured; `daphne` is used in Docker and `channels_redis` as the channel layer backend. See `docker-compose.yml` for a `redis` service.
- Static/media: collectstatic writes to `staticfiles/` and storage uses WhiteNoise + Cloudinary (`django-cloudinary-storage`). Media files are expected on Cloudinary; local dev uses `MEDIA_ROOT` under `media/`.
- Custom user: `AUTH_USER_MODEL = 'accounts.CustomUser'` and `accounts.models.Room` contains custom slug logic (uses `unidecode`) — keep this behavior when modifying room/user code.

Developer workflows (concrete commands and flows)
- Run locally (dev) without Docker (example):
  - Create and activate a virtualenv, install `requirements.txt`.
  - Copy `.env` from `example.env` and set secrets (DB, Cloudinary, Telegram tokens if needed).
  - Run migrations and start Daphne for ASGI:
    - `python manage.py migrate` then `daphne -b 0.0.0.0 -p 8000 my_site.asgi:application` or use `python manage.py runserver` for simple testing.
- With Docker (recommended for parity):
  - `docker-compose up --build` (compose file exposes web on host 8001 and nginx on 8080).
  - Redis is provided by `docker-compose.yml`; `REDIS_HOST` defaults to `redis` in Docker.
- Running bots: `docker-compose` defines a `bot` service that runs `python manage.py run_myregibot` — environment variables from `.env` are required.

Patterns and conventions specific to this project
- i18n: Project defaults to Russian (`LANGUAGE_CODE='ru'`) and uses `django-modeltranslation`. Translation files live under `locale/` and `MODELTRANSLATION_TRANSLATION_FILES` lists modules (e.g., `notes_app.translation`).
- Contract generator: `contract_maker.document_generator` uses constants from `contract_maker.generator_config`. The generator pulls executor details from `.env` keys prefixed with `CONTRACT_MAKER_*` (or fallback to plain keys). Templates are under `contract_maker/doc_templates/` and outputs go to media `contract_output/` unless overridden in settings.
  - When making changes to contract generation, prefer using `generator_config._get_req` to read new config keys so behavior remains consistent.
- WebSockets and Channels:
  - Consumer example: `chat/consumers.py` implements an `AsyncWebsocketConsumer` that relies on `scope['user']` (auth). Use `sync_to_async` for ORM calls or `@database_sync_to_async` patterns. When editing consumers, preserve group naming `chat_{room_slug}` and message shapes (JSON with `message`, `username`).
- Slug and transliteration: `accounts.models.custom_slugify` uses `unidecode` then `slugify`. When adding new slugs or URLs, reuse this helper to avoid inconsistencies.

Where to look for related code (quick reference)
- Settings and env: `my_site/settings.py`, `.env`, `example.env`.
- Runtime scripts: `manage.py` and Docker artifacts `Dockerfile`, `docker-compose.yml`, `DOCKER.md`.
- Channels & consumers: `chat/consumers.py`, `chat/routing.py`.
- Auth and rooms: `accounts/models.py`, `accounts/views.py` (for send_telegram_message usage), `accounts/forms.py`.
- Contract maker: `contract_maker/document_generator.py`, `contract_maker/generator_config.py`, `contract_maker/doc_templates/`.

Examples of code-aware suggestions the AI should make
- Add new environment-driven feature: add key to `example.env`, read via `contract_maker.generator_config._get_req`, and reference in `settings.py` if global.
- Fix a consumer bug: preserve `group_add`/`group_send` naming and return the same JSON fields consumed by front-end (do not rename keys without updating matching templates/JS).
- Changing user model: surface migration impact — update `AUTH_USER_MODEL` reference and provide a migration plan (create new migration, run `makemigrations`, apply).

Quick tests and quality gates
- Any code change that touches models or settings should be followed by `python manage.py makemigrations` and `python manage.py migrate` in dev.
- For WebSocket changes, unit test `chat` consumers with `channels.testing` helpers or run a short local Daphne + Redis and use a simple websocket client.

What NOT to do
- Don't change `AUTH_USER_MODEL` without a clear migration strategy.
- Don't replace Cloudinary storage with a local filesystem storage in production-focused changes; keep `CLOUDINARY_*` env-driven config.

If anything is unclear or you need permissions/credentials (Cloudinary, Telegram, DB), ask the human owner — sensitive secrets are only in `.env` (not checked into git).

If you update this file, keep it short (20–50 lines) and factual — prefer linking to the exact file that demonstrates the behaviour rather than general advice.
