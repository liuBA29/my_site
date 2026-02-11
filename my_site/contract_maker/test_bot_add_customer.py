#!/usr/bin/env python
"""
Тестовый скрипт: добавление клиента через API (как будет вызывать бот).
Запуск: из корня проекта (где manage.py)
  python -m contract_maker.test_bot_add_customer
  или с указанием базового URL:
  python -m contract_maker.test_bot_add_customer https://liuba.site

Потом в боте отправляешь запрос на тот же URL с телом JSON.
"""
import json
import os
import sys

# Подгружаем .env из корня проекта (рядом с manage.py)
try:
    from pathlib import Path
    _root = Path(__file__).resolve().parent.parent
    _env = _root / ".env"
    if _env.exists():
        from dotenv import load_dotenv
        load_dotenv(_env)
except Exception:
    pass

try:
    import requests
except ImportError:
    requests = None

# Базовый URL приложения contract-maker (без завершающего слэша)
BASE_URL = os.environ.get("CONTRACT_MAKER_BASE_URL", "http://127.0.0.1:8000/contract-maker")
# Токен (если в .env задан CONTRACT_MAKER_BOT_TOKEN — передаётся в запросе)
BOT_TOKEN = os.environ.get("CONTRACT_MAKER_BOT_TOKEN", "")


def add_customer(data, base_url=None, token=None):
    url = (base_url or BASE_URL).rstrip("/") + "/api/customer/add/"
    headers = {"Content-Type": "application/json; charset=utf-8"}
    if token:
        headers["X-Bot-Token"] = token
    body = dict(data)
    if token and "token" not in body:
        body["token"] = token
    if requests:
        r = requests.post(url, json=body, headers=headers, timeout=10)
        return r.status_code, r.json() if r.headers.get("content-type", "").startswith("application/json") else {"text": r.text}
    # без requests — через urllib
    import urllib.request
    req = urllib.request.Request(url, data=json.dumps(body).encode("utf-8"), method="POST")
    req.add_header("Content-Type", "application/json; charset=utf-8")
    for k, v in headers.items():
        if k != "Content-Type":
            req.add_header(k, v)
    with urllib.request.urlopen(req, timeout=10) as resp:
        return resp.status, json.loads(resp.read().decode("utf-8"))


if __name__ == "__main__":
    base = (sys.argv[1] if len(sys.argv) > 1 else None) or BASE_URL
    # Пример данных — как будет слать бот
    payload = {
        "org_name": "Тест из бота ООО Рога и копыта",
        "client_type": "legal",
        "rep_name": "Иванов Иван Иванович",
        "rep_position": "директора",
        "address": "г. Минск",
        "unp": "123456789",
    }
    if BOT_TOKEN:
        payload["token"] = BOT_TOKEN
    print("POST", base.rstrip("/") + "/api/customer/add/")
    print("Body:", json.dumps(payload, ensure_ascii=False, indent=2))
    try:
        status, result = add_customer(payload, base_url=base, token=BOT_TOKEN or None)
        print("Status:", status)
        print("Response:", json.dumps(result, ensure_ascii=False, indent=2))
        if result.get("ok") and result.get("id"):
            print("Клиент добавлен, id =", result["id"])
    except Exception as e:
        print("Error:", e)
        sys.exit(1)
