# chat/views.py
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.utils.timezone import now
from django.contrib.auth.models import AnonymousUser
from .models import GuestUser
import json


@csrf_exempt
def set_username(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username', '').strip()
        room_name = data.get('room_name', '').strip()

        request.session['username'] = username

        # Если пользователь не аутентифицирован — сохраняем как GuestUser
        if not request.user.is_authenticated and username:
            ip = get_client_ip(request)

            # Проверяем, существует ли уже такой гость
            exists = GuestUser.objects.filter(ip_address=ip).exists()
            if not exists:
                GuestUser.objects.create(
                    ip_address=ip,
                    username=username,
                    room_name=room_name,
                    created_at=now()
                )

        return JsonResponse({'status': 'ok'})

    elif request.method == 'GET':
        username = request.session.get('username', '')
        return JsonResponse({'username': username})


def get_client_ip(request):
    """Получить IP-адрес клиента из запроса"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def lobby(request):
    if request.user.is_authenticated:
        username = request.user.username
        room_name = ''
        return render(request, 'chat/lobby.html', {
            'username': username,
            'room_name': room_name,
        })
    else:
        ip = get_client_ip(request)
        guest = GuestUser.objects.filter(ip_address=ip).order_by('-created_at').first()

        if guest:
            username = guest.username
            room_name = guest.room_name
            # Сохраняем в сессию, если нужно
            request.session['username'] = username
        else:
            username = ''
            room_name = ''

        return render(request, 'chat/lobby.html', {
            'username': username,
            'room_name': room_name,
        })



