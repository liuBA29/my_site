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

# Минимальные переменные для collectstatic при сборке (в рантайме переопределяются через env_file)
ENV DJANGO_SETTINGS_MODULE=my_site.settings
ENV SECRET_KEY=build-time-placeholder
ENV ALLOWED_HOSTS=*
ENV DEBUG=0

# Собираем статические файлы (при сборке контейнера)
RUN python manage.py collectstatic --noinput

# Указываем порт, который будет использоваться приложением
EXPOSE 8000

# Указываем команду запуска daphne
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "my_site.asgi:application"]

