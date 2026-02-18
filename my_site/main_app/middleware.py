import os
from django.utils.timezone import now
from dotenv import load_dotenv
from .utils import get_client_ip

load_dotenv()  # Загружает переменные из .env файла

EXCLUDED_IPS = os.getenv('EXCLUDED_IPS', '').split(',')

# Пути, которые НЕ нужно логировать
EXCLUDED_PATHS = [
    '/admin/',
    '/favicon.ico',
    '/robots.txt',
    '/sitemap.xml',
    '/mysitemap.xml',
]

class PageViewMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Получаем IP
        ip = get_client_ip(request)

        # Пропускаем, если IP в исключениях
        if ip in EXCLUDED_IPS:
            return self.get_response(request)

        # Убрана логика обнаружения Safari и отправки уведомлений

        response = self.get_response(request)

        path = request.path

        # Логируем все страницы, кроме исключений
        should_log = (
            # Не статические файлы
            not path.startswith('/static/') and
            not path.startswith('/media/') and
            # Не исключенные пути
            path not in EXCLUDED_PATHS and
            # Не начинается с исключенных префиксов
            not any(path.startswith(excluded) for excluded in EXCLUDED_PATHS) and
            # Только успешные ответы (200)
            response.status_code == 200
        )

        if should_log:
            try:
                # Импортируем модели внутри метода
                from .models import PageView, PageVisitLog

                # Обновление/создание записи просмотров
                view, _ = PageView.objects.get_or_create(path=path)
                view.views_count += 1
                view.last_viewed = now()  # Используем существующее поле из модели
                view.save()

                # Запись в лог
                PageVisitLog.objects.create(path=path, ip_address=ip)
            except Exception as e:
                # Игнорируем ошибки логирования, чтобы не сломать сайт
                print(f"Ошибка логирования посещения: {e}")

        return response
