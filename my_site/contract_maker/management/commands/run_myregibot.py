# Бот @myregibot: long polling, по команде «добавь клиента …» создаёт клиента в contract_maker.
# Запуск: python manage.py run_myregibot
# Токен: TELEGRAM_BOT_TOKEN из .env (тот же, что для уведомлений о регистрации).

import re
import time
import requests
from django.core.management.base import BaseCommand
from django.conf import settings

from contract_maker.models import Customer


# Фразы, после которых идёт название организации или ФИО (регистронезависимо)
ADD_CUSTOMER_PATTERNS = [
    r"добавь\s+клиента\s+(.+)",
    r"добавьте\s+клиента\s+(.+)",
    r"добавить\s+клиента\s+(.+)",
    r"создай\s+клиента\s+(.+)",
    r"создайте\s+клиента\s+(.+)",
    r"создать\s+клиента\s+(.+)",
    r"зарегистрируй\s+клиента\s+(.+)",
    r"зарегистрируй\s+компанию\s+(.+)",
    r"добавь\s+компанию\s+(.+)",
    r"add\s+customer\s+(.+)",
]
COMPILED = [re.compile(p, re.IGNORECASE) for p in ADD_CUSTOMER_PATTERNS]


def extract_org_name(text):
    """Если текст — запрос на добавление клиента, вернуть название; иначе None."""
    if not text or not isinstance(text, str):
        return None
    t = text.strip()
    for pat in COMPILED:
        m = pat.match(t)
        if m:
            return m.group(1).strip()
    return None


def send_telegram_reply(token, chat_id, text):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        r = requests.post(url, json={"chat_id": chat_id, "text": text}, timeout=10)
        r.raise_for_status()
    except requests.RequestException as e:
        return False
    return True


class Command(BaseCommand):
    help = (
        "Запуск бота @myregibot: слушает сообщения в Telegram, "
        "по фразам «добавь клиента …» добавляет клиента в contract_maker."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--poll-interval",
            type=float,
            default=1.0,
            help="Пауза между опросами getUpdates (сек). По умолчанию 1.",
        )

    def handle(self, *args, **options):
        token = getattr(settings, "TELEGRAM_BOT_TOKEN", None)
        if not token:
            self.stderr.write(
                self.style.ERROR("TELEGRAM_BOT_TOKEN не задан в .env. Добавьте переменную и перезапустите.")
            )
            return

        # Разрешённые chat_id: для бота можно задать свой (личный чат), отдельно от TELEGRAM_CHAT_ID (уведомления в группу)
        allowed_raw = (
            getattr(settings, "TELEGRAM_BOT_ALLOWED_CHAT_IDS", None)
            or getattr(settings, "TELEGRAM_BOT_ALLOWED_CHAT_ID", None)
            or getattr(settings, "TELEGRAM_CHAT_ID", None)
        )
        if not allowed_raw:
            self.stderr.write(
                self.style.ERROR(
                    "Не задан разрешённый chat_id. В .env укажите один из: TELEGRAM_BOT_ALLOWED_CHAT_ID (ваш user id в личке с ботом), "
                    "TELEGRAM_BOT_ALLOWED_CHAT_IDS (несколько через запятую) или TELEGRAM_CHAT_ID. Узнать id: @userinfobot в Telegram."
                )
            )
            return
        allowed_ids = set()
        for part in str(allowed_raw).replace(",", " ").split():
            try:
                allowed_ids.add(str(int(part.strip())))
            except (TypeError, ValueError):
                pass
        if not allowed_ids:
            self.stderr.write(self.style.ERROR("TELEGRAM_BOT_ALLOWED_CHAT_ID / TELEGRAM_CHAT_ID должны быть числом (или числа через запятую)."))
            return

        poll_interval = options["poll_interval"]
        url = f"https://api.telegram.org/bot{token}/getUpdates"
        offset = None
        self.stdout.write(
            f"Бот @myregibot запущен. Отвечает только в чатах: {', '.join(sorted(allowed_ids))}. Ctrl+C — выход."
        )

        while True:
            try:
                params = {"timeout": 30}
                if offset is not None:
                    params["offset"] = offset
                resp = requests.get(url, params=params, timeout=35)
                data = resp.json()
                if not data.get("ok"):
                    self.stderr.write(f"Telegram API error: {data}")
                    time.sleep(poll_interval)
                    continue

                for upd in data.get("result", []):
                    offset = upd["update_id"] + 1
                    msg = upd.get("message") or upd.get("edited_message")
                    if not msg:
                        continue
                    text = (msg.get("text") or "").strip()
                    chat_id = msg.get("chat", {}).get("id")
                    if not text or chat_id is None:
                        continue

                    # Лог: каждое входящее сообщение (чтобы в docker logs видеть chat_id и текст)
                    self.stdout.write(f"[msg] chat_id={chat_id} text={text[:50]!r}")

                    # Отвечаем только разрешённым чатам (хозяину бота)
                    if str(chat_id) not in allowed_ids:
                        self.stdout.write(
                            f"[skip] chat_id {chat_id} не в разрешённых (разрешены: {', '.join(sorted(allowed_ids))}). "
                            "Добавь этот id в TELEGRAM_BOT_ALLOWED_CHAT_ID в .env и перезапусти бота."
                        )
                        continue

                    org_name = (extract_org_name(text) or "").strip()
                    if not org_name:
                        self.stdout.write(f"[skip] не команда «добавь клиента …»: {text[:50]!r}")
                        continue
                    org_name = org_name[:255]
                    try:
                        customer, created = Customer.objects.get_or_create(
                            org_name=org_name,
                            defaults={
                                "client_type": Customer.CLIENT_TYPE_LEGAL,
                                "created_by": None,
                            },
                        )
                        if created:
                            reply = f"Клиент «{customer.org_name}» добавлен в базу (id={customer.pk})."
                        else:
                            reply = f"Клиент «{customer.org_name}» уже есть в базе (id={customer.pk})."
                        self.stdout.write(f"[ok] {reply}")
                    except Exception as e:
                        reply = f"Ошибка при добавлении клиента: {e}"
                        self.stderr.write(f"[error] {e}")
                    send_telegram_reply(token, chat_id, reply)

            except requests.RequestException as e:
                self.stderr.write(f"Request error: {e}")
            except KeyboardInterrupt:
                self.stdout.write("Выход.")
                break
            except Exception as e:
                self.stderr.write(f"Error: {e}")

            time.sleep(poll_interval)
