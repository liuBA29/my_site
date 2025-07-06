# accounts/views.py
import requests
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from django.contrib import messages
from .models import Room
from django.utils.translation import gettext_lazy as _




def send_telegram_message(text):
    token = settings.TELEGRAM_BOT_TOKEN
    chat_id = settings.TELEGRAM_CHAT_ID
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {
        'chat_id': chat_id,
        'text': text
    }
    try:
        response = requests.post(url, data=data)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Ошибка отправки в Telegram: {e}")


def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()

            # 🛠️ Создаём комнату для нового пользователя
            room_name = f"{user.username}room"
            room, created = Room.objects.get_or_create(name=room_name)

            # 💞 Привязываем комнату к пользователю
            user.rooms.add(room)

            login(request, user)
            messages.success(request, 'Регистрация прошла успешно!')

            # Отправляем уведомление в телеграм
            send_telegram_message(f"Новый пользователь зарегистрировался: {user.username} (ID: {user.id})")

            return redirect('main_app:contact')
        else:
            print("❌ Ошибка валидации формы:")
            print(form.errors)
            messages.error(request, f"Ошибка регистрации: {form.errors.as_text()}")
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})



def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Вы успешно вошли, {user} !')
            return redirect('main_app:contact')  # куда перенаправлять после входа
    else:
        form = CustomAuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, 'Вы вышли из системы.')
    return redirect('main_app:home')
