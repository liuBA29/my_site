"""
Утилиты для main_app
"""
from django.conf import settings


def get_client_ip(request):
    """
    Получение IP адреса клиента с учетом прокси-серверов.
    
    Args:
        request: Django HttpRequest объект или None
        
    Returns:
        str: IP адрес клиента или None если не удалось определить или request=None
    """
    if not request:
        return None
    
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        # Берем первый IP из списка (реальный клиент)
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
