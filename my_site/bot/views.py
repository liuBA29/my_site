# HTTP API для ботов и внешних клиентов (добавить клиента и т.д.).

import json

from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .actions.add_customer import add_customer_from_payload


def _json_response(data, status=200):
    return HttpResponse(
        json.dumps(data, ensure_ascii=False),
        content_type="application/json; charset=utf-8",
        status=status,
    )


@csrf_exempt
@require_http_methods(["POST"])
def api_add_customer(request):
    """
    API для бота: добавить клиента. POST JSON.
    Тело: {"org_name": "ООО Рога", "client_type": "legal", "rep_name": "...", ...}
    Обязательно: CONTRACT_MAKER_BOT_TOKEN в настройках и заголовок X-Bot-Token или поле "token" в JSON.
    """
    try:
        body = json.loads(request.body) if request.body else {}
    except json.JSONDecodeError:
        return _json_response({"ok": False, "error": "Invalid JSON"}, status=400)

    token = (getattr(settings, "CONTRACT_MAKER_BOT_TOKEN", None) or "").strip()
    if not token:
        return _json_response(
            {"ok": False, "error": "API disabled: CONTRACT_MAKER_BOT_TOKEN not set"},
            status=403,
        )
    header_token = request.headers.get("X-Bot-Token")
    body_token = body.get("token")
    if header_token != token and body_token != token:
        return _json_response({"ok": False, "error": "Invalid token"}, status=403)

    # В payload не передаём token в логику создания клиента
    data = {k: v for k, v in body.items() if k != "token"}
    customer, created, error = add_customer_from_payload(data)
    if error:
        return _json_response({"ok": False, "error": error}, status=400)
    return _json_response({
        "ok": True,
        "id": customer.pk,
        "org_name": customer.org_name,
    })
