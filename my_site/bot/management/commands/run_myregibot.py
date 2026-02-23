# Бот @myregibot: long polling, по команде «добавь клиента …» создаёт клиента в contract_maker.
# Запуск: python manage.py run_myregibot
# Токен: TELEGRAM_BOT_TOKEN из .env (тот же, что для уведомлений о регистрации).

import re
import time
import requests
from django.core.management.base import BaseCommand
from django.conf import settings

from bot.telegram import send_telegram
from bot.actions.add_customer import add_customer_from_payload


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

# «Добавь договор» и похожее — подсказать, что пока только клиенты
ADD_CONTRACT_HINT = re.compile(
    r"^(добавь|добавить|создай|создать)\s+(договор|акт|контракт)",
    re.IGNORECASE,
)

# Кнопки под сообщением (ReplyKeyboard)
ADD_CUSTOMER_BUTTON = "➕ Добавить клиента"
KEYBOARD_COMMANDS = {
    "keyboard": [[ADD_CUSTOMER_BUTTON]],
    "resize_keyboard": True,
}

# Приветствия — отвечаем «Привет!»
GREETING_WORDS = (
    "привет", "приветик", "здравствуй", "здравствуйте", "здаров", "хай", "hello",
    "hi", "hey", "добрый день", "добрый вечер", "доброе утро", "доброй ночи",
)
GREETING_RE = re.compile(
    r"^(" + "|".join(re.escape(w) for w in GREETING_WORDS) + r")[\s!?.,]*$",
    re.IGNORECASE,
)


def is_greeting(text):
    """Сообщение — приветствие (одно слово/фраза из списка или начинается с приветствия)."""
    if not text or not isinstance(text, str):
        return False
    t = text.strip()
    if not t:
        return False
    # Точное совпадение (с пунктуацией в конце) или первое слово — приветствие
    if GREETING_RE.match(t):
        return True
    t_lower = t.lower()
    if t_lower in GREETING_WORDS:
        return True
    first_word = t_lower.split()[0].rstrip("!?.,;:")
    return first_word in GREETING_WORDS


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


class Command(BaseCommand):
    help = (
        "Запуск бота @myregibot: слушает сообщения в Telegram, "
        "отвечает «Привет!» на приветствие, по фразам «добавь клиента …» добавляет клиента в contract_maker."
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
        if token:
            token = (token or "").strip()
        if not token:
            self.stderr.write(
                self.style.ERROR(
                    "TELEGRAM_BOT_TOKEN не задан. Проверьте: .env лежит в папке с manage.py, "
                    "строка TELEGRAM_BOT_TOKEN=токен без кавычек и пробелов вокруг =."
                )
            )
            return

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
            self.stderr.write(
                self.style.ERROR("TELEGRAM_BOT_ALLOWED_CHAT_ID / TELEGRAM_CHAT_ID должны быть числом (или числа через запятую).")
            )
            return

        poll_interval = options["poll_interval"]
        url = f"https://api.telegram.org/bot{token}/getUpdates"
        offset = None
        token_preview = f"{token[:6]}...{token[-4:]}" if len(token) > 12 else "***"
        self.stdout.write(
            f"Токен: {token_preview}. Разрешённые чаты: {', '.join(sorted(allowed_ids))}. Ctrl+C — выход."
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

                    self.stdout.write(f"[msg] chat_id={chat_id} text={text[:50]!r}")

                    if str(chat_id) not in allowed_ids:
                        self.stdout.write(
                            f"[skip] chat_id {chat_id} не в разрешённых (разрешены: {', '.join(sorted(allowed_ids))}). "
                            "Добавь этот id в TELEGRAM_BOT_ALLOWED_CHAT_ID в .env и перезапусти бота."
                        )
                        continue

                    if is_greeting(text):
                        send_telegram("Привет!", chat_id=chat_id, reply_markup=KEYBOARD_COMMANDS)
                        self.stdout.write("[greeting] ответ «Привет!» + кнопки")
                        continue

                    # Нажатие «Добавить клиента» или фраза без названия — подсказка
                    t_strip = text.strip()
                    t_lower = t_strip.lower()
                    if t_strip in (ADD_CUSTOMER_BUTTON, "Добавить клиента") or t_lower in ("добавить клиента", "добавь клиента"):
                        hint = (
                            "Напиши: добавь клиента <название>, например:\n"
                            "добавь клиента ООО Ромашка"
                        )
                        send_telegram(hint, chat_id=chat_id, reply_markup=KEYBOARD_COMMANDS)
                        self.stdout.write("[hint] подсказка «добавить клиента» + кнопки")
                        continue

                    org_name = (extract_org_name(text) or "").strip()
                    if not org_name:
                        if ADD_CONTRACT_HINT.match(text):
                            hint = (
                                "Пока умею только добавлять клиентов. Напиши, например: «Добавь клиента ООО Ромашка». "
                                "Договор создаётся на сайте liuba.site в разделе Договоры."
                            )
                            send_telegram(hint, chat_id=chat_id)
                            self.stdout.write("[hint] отправлена подсказка про договор")
                        else:
                            self.stdout.write(f"[skip] не команда «добавь клиента …»: {text[:50]!r}")
                        continue

                    customer, created, error = add_customer_from_payload({"org_name": org_name[:255]})
                    if error:
                        reply = f"Ошибка при добавлении клиента: {error}"
                        self.stderr.write(f"[error] {error}")
                    else:
                        if created:
                            reply = f"Клиент «{customer.org_name}» добавлен в базу (id={customer.pk})."
                        else:
                            reply = f"Клиент «{customer.org_name}» уже есть в базе (id={customer.pk})."
                        self.stdout.write(f"[ok] {reply}")
                    send_telegram(reply, chat_id=chat_id)

            except requests.RequestException as e:
                self.stderr.write(f"Request error: {e}")
            except KeyboardInterrupt:
                self.stdout.write("Выход.")
                break
            except Exception as e:
                self.stderr.write(f"Error: {e}")

            time.sleep(poll_interval)
