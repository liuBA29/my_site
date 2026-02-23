# Реализация отправки в Telegram вынесена в приложение bot (конструктор ботов/ИИ-ассистентов).
# Здесь — обратная совместимость: старый код импортирует send_telegram из accounts.telegram_utils.

from bot.telegram import send_telegram

__all__ = ["send_telegram"]
