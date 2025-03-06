import os
from dotenv import load_dotenv
print(os.path.exists(".env"))  # Должно вывести True
load_dotenv()

print(os.getenv("CLOUDINARY_CLOUD_NAME"))  # Должно вывести имя облака
print(os.getenv("CLOUDINARY_API_KEY"))  # Должен вывести API-ключ