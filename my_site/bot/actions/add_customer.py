# Действие «добавить клиента» — общая логика для Telegram-бота и HTTP API.
# Модель Customer живёт в contract_maker; здесь только бизнес-логика создания из payload.

from contract_maker.models import Customer


def add_customer_from_payload(data):
    """
    Создать или найти клиента по данным из словаря (JSON API / парсинг команды бота).

    :param data: dict с ключами org_name (обязательно), client_type, rep_position, rep_name, basis,
                 short_name, address, unp, okpo, iban (все опционально).
    :return: (customer, created, None) при успехе или (None, None, error_message) при ошибке.
    """
    org_name = (data.get("org_name") or "").strip()
    if not org_name:
        return None, None, "org_name is required"

    client_type = data.get("client_type") or Customer.CLIENT_TYPE_LEGAL
    if client_type not in (Customer.CLIENT_TYPE_INDIVIDUAL, Customer.CLIENT_TYPE_LEGAL):
        client_type = Customer.CLIENT_TYPE_LEGAL

    try:
        customer, created = Customer.objects.get_or_create(
            org_name=org_name[:255],
            defaults={
                "client_type": client_type,
                "rep_position": (data.get("rep_position") or "").strip()[:100],
                "rep_name": (data.get("rep_name") or "").strip()[:255],
                "basis": (data.get("basis") or "Устава").strip()[:255],
                "short_name": (data.get("short_name") or "").strip()[:100],
                "address": (data.get("address") or "").strip()[:500],
                "unp": (data.get("unp") or "").strip()[:20],
                "okpo": (data.get("okpo") or "").strip()[:20],
                "iban": (data.get("iban") or "").strip()[:50],
                "created_by": None,
            },
        )
        return customer, created, None
    except Exception as e:
        return None, None, str(e)
