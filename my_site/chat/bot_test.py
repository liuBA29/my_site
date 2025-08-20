import requests
import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env
load_dotenv()

# Берём токен из переменной окружения
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
URL = f"https://api.telegram.org/bot{TOKEN}/getUpdates"

response = requests.get(URL)
print(response.json())