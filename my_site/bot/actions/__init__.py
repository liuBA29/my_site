# Действия/хендлеры бота — переиспользуемая логика (добавить клиента, позже — другие команды).
# Вызываются из run_myregibot и из HTTP API.

from .add_customer import add_customer_from_payload

__all__ = ["add_customer_from_payload"]
