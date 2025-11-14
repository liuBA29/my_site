# Структура проекта my_site

```
my_site/
│
├── accounts/                    # Приложение для аутентификации
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py                 # Формы регистрации и входа
│   ├── models.py                # Модели пользователей и комнат
│   ├── urls.py
│   ├── views.py                 # Представления (регистрация, вход, телеграм-бот)
│   └── migrations/
│       └── 0001_initial.py
│
├── agregator/                   # Приложение агрегатора
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
│
├── chat/                        # Приложение чата (WebSocket)
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── bot_test.py
│   ├── consumers.py             # WebSocket consumers для Django Channels
│   ├── models.py                # Модели сообщений
│   ├── routing.py               # WebSocket routing
│   ├── tests.py
│   ├── urls.py
│   └── views.py
│
├── main_app/                    # Основное приложение портфолио
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── middleware.py            # Пользовательские middleware
│   ├── models.py                # Модели проектов, софта, контактов
│   ├── sitemaps.py              # Sitemap для SEO
│   ├── tests.py
│   ├── translation.py           # Переводы
│   ├── urls.py
│   └── views.py                 # Представления главных страниц
│
├── notes_app/                   # Приложение заметок
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── tests.py
│   ├── translation.py
│   ├── urls.py
│   └── views.py
│
├── my_site/                     # Основная конфигурация Django
│   ├── __init__.py
│   ├── asgi.py                  # ASGI конфигурация для WebSocket
│   ├── settings.py              # Настройки проекта
│   ├── urls.py                  # Главный urls.py
│   └── wsgi.py                  # WSGI конфигурация
│
├── templates/                    # HTML шаблоны
│   ├── base.html                # Базовый шаблон
│   ├── accounts/
│   │   ├── login.html
│   │   └── register.html
│   ├── agregator/
│   │   └── book_list.html
│   ├── chat/
│   │   ├── lobby.html
│   │   └── _lobby_partial.html
│   ├── main_app/
│   │   ├── contact.html
│   │   ├── descriptions.html
│   │   ├── index.html
│   │   ├── my_projects.html
│   │   ├── page_view.html
│   │   ├── project_detail.html
│   │   ├── test_useful.html
│   │   ├── useful_soft.html
│   │   ├── useful_soft_detail.html
│   │   └── visits_log.html
│   └── notes/
│       ├── article_detail.html
│       ├── index.html
│       ├── note_confirm_delete.html
│       ├── note_detail.html
│       ├── note_form.html
│       └── note_list.html
│
├── static/                       # Статические файлы (CSS, JS)
│   ├── CSS/
│   │   ├── styles.css           # Основные стили
│   │   ├── styles_light.css     # Упрощенные стили для iOS
│   │   └── styles_mint.css      # Мятная тема
│   ├── downloads/
│   │   └── mantra-player-installer.zip
│   └── JS/
│       ├── lobby.js             # JavaScript для чата
│       └── main.js              # Основной JavaScript
│
├── staticfiles/                  # Собранные статические файлы (collectstatic)
│   ├── admin/                   # Статические файлы Django Admin
│   ├── cloudinary/              # Статические файлы Cloudinary
│   ├── CSS/
│   ├── downloads/
│   ├── JS/
│   └── modeltranslation/        # Статические файлы для переводов
│
├── media/                        # Медиа файлы (загружаемые пользователями)
│   ├── client_images/           # Изображения клиентов
│   ├── downloads/               # Файлы для скачивания
│   └── projects/                # Изображения и видео проектов
│
├── locale/                       # Файлы локализации
│   └── ru/
│       └── LC_MESSAGES/
│           ├── django.mo
│           ├── django.po
│           ├── djangojs.mo
│           └── djangojs.po
│
├── manage.py                     # Django management script
├── requirements.txt              # Зависимости проекта
├── requirements_all.txt          # Все зависимости
├── Dockerfile                    # Docker конфигурация
├── docker-compose.yml            # Docker Compose конфигурация
├── nginx.conf                    # Конфигурация Nginx
├── robots.txt                    # Robots.txt для SEO
├── sitemap-handmade.xml          # Ручной sitemap
├── mysitemap.xml                 # Автоматический sitemap
├── db.sqlite3                    # База данных SQLite
└── remotedb.sqlite3              # Удаленная база данных (бэкап)

```

## Основные компоненты:

### Приложения Django:
- **accounts** - Аутентификация пользователей, регистрация, телеграм-бот уведомлений
- **chat** - WebSocket чат с Django Channels и Redis
- **main_app** - Основное портфолио: проекты, полезный софт, контакты
- **notes_app** - Приложение для заметок/статей
- **agregator** - Агрегатор контента

### Технологии:
- **Django** - основной фреймворк
- **Django Channels** - WebSocket для чата
- **Redis** - для WebSocket
- **Daphne** - ASGI сервер
- **Cloudinary** - для хранения изображений
- **Django Modeltranslation** - для мультиязычности

### Особенности:
- Адаптивный дизайн с поддержкой старых iPhone
- Две темы: светлая (основная) и упрощенная для iOS
- Мультиязычность (русский/английский)
- WebSocket чат в реальном времени
- Интеграция с Telegram Bot API для уведомлений
- SEO оптимизация (sitemap, robots.txt)

