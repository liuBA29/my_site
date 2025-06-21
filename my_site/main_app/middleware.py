import os
from django.utils.timezone import now
from dotenv import load_dotenv

load_dotenv()  # Загружает переменные из .env файла

EXCLUDED_IPS = os.getenv('EXCLUDED_IPS', '').split(',')

# Пути, по которым ведётся учёт просмотров
TRACKED_PATHS = [
    '/',
    '/useful-soft/', '/useful-soft/mantra-player/', '/useful-soft/email-sender/',
    '/my-projects/', '/project/asterisk-call-monitoring/',
    '/contact/',
]

class PageViewMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Получаем IP
        ip = self.get_client_ip(request)

        # Пропускаем, если IP в исключениях
        if ip in EXCLUDED_IPS:
            return self.get_response(request)

        response = self.get_response(request)

        path = request.path

        if (
            path in TRACKED_PATHS and
            path not in ['/admin/', '/favicon.ico'] and
            not path.startswith('/static/')
        ):
            # Импортируем модели внутри метода
            from .models import PageView, PageVisitLog

            # Обновление/создание записи просмотров
            view, _ = PageView.objects.get_or_create(path=path)
            view.views_count += 1
            view.last_viewed_at = now()
            view.last_viewed_ip = ip
            view.save()

            # Запись в лог
            PageVisitLog.objects.create(path=path, ip_address=ip)

        return response

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')
