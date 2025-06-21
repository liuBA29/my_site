#Dockerfile

# Используем базовый Python-образ
FROM python:3.10-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем зависимости проекта
COPY requirements.txt /app/requirements.txt

# Устанавливаем зависимости
RUN pip install --upgrade pip \
    && pip install -r requirements.txt \
    && pip install daphne


# Копируем все файлы проекта
COPY . /app

# Загружаем переменные окружения из .env (если используешь .env для Cloudinary)
# Устанавливаем переменные окружения для Cloudinary
ENV CLOUDINARY_CLOUD_NAME=your_cloud_name
ENV CLOUDINARY_API_KEY=your_api_key
ENV CLOUDINARY_API_SECRET=your_api_secret


# Собираем статические файлы (при сборке контейнера)
RUN python manage.py collectstatic --noinput

# Указываем порт, который будет использоваться приложением
EXPOSE 8000

# Указываем команду запуска daphne
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "my_site.asgi:application"]

