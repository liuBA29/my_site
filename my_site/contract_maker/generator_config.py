# Реквизиты исполнителя (самозанятой) из .env / Django settings
#
# Данные для договора берутся из .env (например строки 30–35). Поддерживаются ключи:
#   CONTRACT_MAKER_FULL_NAME  или  FULL_NAME   — ФИО исполнителя
#   CONTRACT_MAKER_SHORT_NAME или  SHORT_NAME  — подпись в реквизитах (если пусто — FULL_NAME)
#   CONTRACT_MAKER_INN        или  INN         — ИНН
#   CONTRACT_MAKER_ADDRESS    или  ADDRESS     — адрес
#   CONTRACT_MAKER_BASIS     или  BASIS       — на основании чего действуете
#   CONTRACT_MAKER_BANK_DATA или  BANK_DATA   — банковские реквизиты (\\n = перенос строки)
#
# Порядок: CONTRACT_MAKER_* из .env → вариант без префикса → settings → дефолт (пусто).

import os
from pathlib import Path

from django.conf import settings
from dotenv import load_dotenv

BASE_DIR = Path(settings.BASE_DIR)
load_dotenv(BASE_DIR / ".env")


def _get_req(env_key, env_alt, settings_key, default):
    """Подставить реквизит: .env (основной ключ) → .env (альт) → settings → default."""
    v = os.getenv(env_key) or os.getenv(env_alt)
    if v is not None and v.strip():
        return v.strip()
    return getattr(settings, settings_key, None) or default


# Реквизиты исполнителя — только из .env (дефолты пустые/минимальные)
FULL_NAME = _get_req("CONTRACT_MAKER_FULL_NAME", "FULL_NAME", "CONTRACT_MAKER_FULL_NAME", "").strip()
SHORT_NAME = (_get_req("CONTRACT_MAKER_SHORT_NAME", "SHORT_NAME", "CONTRACT_MAKER_SHORT_NAME", "").strip() or FULL_NAME)
INN = _get_req("CONTRACT_MAKER_INN", "INN", "CONTRACT_MAKER_INN", "")
ADDRESS = _get_req("CONTRACT_MAKER_ADDRESS", "ADDRESS", "CONTRACT_MAKER_ADDRESS", "")
BASIS = _get_req("CONTRACT_MAKER_BASIS", "BASIS", "CONTRACT_MAKER_BASIS", "")
_bank = _get_req("CONTRACT_MAKER_BANK_DATA", "BANK_DATA", "CONTRACT_MAKER_BANK_DATA", "")
BANK_DATA = (_bank or "").replace("\\n", "\n").strip()

# Папки для генерации (в MEDIA или в отдельной директории приложения)
CONTRACT_MAKER_OUTPUT = getattr(settings, "CONTRACT_MAKER_OUTPUT", None)
if CONTRACT_MAKER_OUTPUT:
    OUTPUT_DIR = Path(CONTRACT_MAKER_OUTPUT)
else:
    OUTPUT_DIR = Path(settings.MEDIA_ROOT) / "contract_output"
TEMPLATES_DIR = Path(__file__).resolve().parent / "doc_templates"
