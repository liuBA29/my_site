from .models import PageView, PageVisitLog
from django.utils.deprecation import MiddlewareMixin
from django.utils.timezone import now
from dotenv import load_dotenv
import os

load_dotenv()  # Загружает переменные из .env файла

EXCLUDED_IPS = os.getenv('EXCLUDED_IPS', '').split(',')


# Список IP-адресов, с которых не следует учитывать посещения (например, твой IP)

TRACKED_PATHS = ['/', '/useful-soft/', '/my-projects/', '/contact/']

class PageViewMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response



    def __call__(self, request):
        # Получаем IP-адрес клиента
        ip = self.get_client_ip(request)

        # Если IP-адрес в списке исключений, пропускаем обработку
        if ip in EXCLUDED_IPS:
            return self.get_response(request)

        # Обрабатываем остальные запросы
        response = self.get_response(request)

        path = request.path

        # Проверяем, что путь в списке отслеживаемых
        if path in TRACKED_PATHS and path not in ['/admin/', '/favicon.ico'] and not path.startswith('/static/'):
            view, _ = PageView.objects.get_or_create(path=path)
            view.views_count += 1
            view.last_viewed_at = now()
            view.last_viewed_ip = ip
            view.save()

            PageVisitLog.objects.create(path=path, ip_address=ip)

        return response



    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')