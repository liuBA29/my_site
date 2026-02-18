# accounts/signals.py
import logging

from django.contrib.auth.signals import user_logged_in, user_login_failed
from django.dispatch import receiver
from django.utils import timezone

from main_app.utils import get_client_ip
from .views import send_telegram_message

logger = logging.getLogger(__name__)


@receiver(user_logged_in)
def admin_login_notification(sender, request, user, **kwargs):
    """
    Отправляет уведомление в Telegram о входе пользователя в админку.
    """
    # Проверяем, что пользователь является staff (обычно это означает вход в админку)
    # Также проверяем, что запрос идет из админки (по рефереру или пути)
    referer = request.META.get('HTTP_REFERER', '')
    path = request.path
    
    # Проверяем, что это вход в админку (staff пользователь и запрос из админки)
    is_admin_login = (
        (user.is_staff or user.is_superuser) and 
        ('/admin/login' in referer or path.startswith('/admin/'))
    )
    
    if is_admin_login:
        # Получаем IP адрес
        ip_address = get_client_ip(request)
        
        # Формируем сообщение
        current_time = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
        message = (
            f"🔐 Вход в админку\n\n"
            f"👤 Пользователь: {user.username}\n"
            f"📧 Email: {user.email or 'не указан'}\n"
            f"🔑 Тип: {'Суперпользователь' if user.is_superuser else 'Staff'}\n"
            f"🌐 IP: {ip_address}\n"
            f"📅 Время: {current_time}"
        )
        
        try:
            send_telegram_message(message)
        except Exception:
            logger.exception("Ошибка отправки уведомления о входе в Telegram")


@receiver(user_login_failed)
def admin_login_failed_notification(sender, credentials, request, **kwargs):
    """
    Отправляет уведомление в Telegram о неудачной попытке входа в админку.
    """
    # Проверяем, что запрос идет к админке
    path = request.path
    referer = request.META.get('HTTP_REFERER', '')
    
    if path.startswith('/admin/login') or '/admin/login' in referer:
        # Получаем IP адрес
        ip_address = get_client_ip(request)
        
        # Получаем имя пользователя из credentials
        username = credentials.get('username', 'неизвестно')
        
        # Получаем текущее время
        current_time = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Формируем сообщение
        message = (
            f"⚠️ Неудачная попытка входа в админку\n\n"
            f"👤 Имя пользователя: {username}\n"
            f"🌐 IP: {ip_address}\n"
            f"🔗 Путь: {path}\n"
            f"📅 Время: {current_time}"
        )
        
        try:
            send_telegram_message(message)
        except Exception:
            logger.exception("Ошибка отправки уведомления о неудачной попытке входа в Telegram")

