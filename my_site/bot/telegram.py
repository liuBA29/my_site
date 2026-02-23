# Базовый конструктор: отправка сообщений в Telegram.
# Переиспользуется для уведомлений с сайта, для ответов бота, для будущих ботов/ИИ-ассистентов.
# При любой ошибке (бот недоступен, неверный токен, сеть, таймаут) исключения не пробрасываются — сайт работает дальше.

import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


def send_telegram(text, chat_id=None, reply_markup=None):
    """
    Отправить сообщение в Telegram.

    :param text: Текст сообщения.
    :param chat_id: Куда отправить. Если None — используется settings.TELEGRAM_CHAT_ID (уведомления).
    :param reply_markup: Опционально — клавиатура (dict для ReplyKeyboardMarkup/InlineKeyboardMarkup).
    :return: True при успехе, False при ошибке или если не заданы токен/chat_id.
    """
    try:
        token = getattr(settings, "TELEGRAM_BOT_TOKEN", None)
        if not token:
            logger.warning("TELEGRAM_BOT_TOKEN не задан — сообщение в Telegram не отправлено")
            return False

        if chat_id is None:
            chat_id = getattr(settings, "TELEGRAM_CHAT_ID", None)
        if chat_id is None:
            logger.warning("TELEGRAM_CHAT_ID не задан и chat_id не передан — сообщение не отправлено")
            return False

        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {"chat_id": chat_id, "text": str(text)}
        if reply_markup is not None:
            payload["reply_markup"] = reply_markup
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        return True
    except Exception:
        logger.exception(
            "Telegram: сообщение не отправлено (бот недоступен, неверный токен, сеть или таймаут). Сайт работает дальше."
        )
        return False
