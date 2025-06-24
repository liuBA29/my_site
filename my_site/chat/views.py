# chat/views.py

from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from .models import GuestUser, Room
import json


@csrf_exempt
def set_username(request):
    """
    Сохраняет или обновляет имя гостя по IP-адресу
    """
    if request.method != "POST":
        return JsonResponse({"error": "Метод не разрешён"}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Неверный JSON"}, status=400)

    username = data.get("username")
    if not username:
        return JsonResponse({"error": "Имя обязательно"}, status=400)

    ip = get_client_ip(request)
# !!Надо чтоб еще и комната создавалась под него! она создается в модели Romm

    guest, created = GuestUser.objects.get_or_create(
        ip_address=ip,
        defaults={'username': username}
    )
    if not created:
        guest.username = username
        guest.save()

    request.session['guest_username'] = guest.username

    return JsonResponse({"message": "Имя сохранено", "username": guest.username})


@require_GET
def check_guest_user(request):
    """
    Проверяет, есть ли гость по IP и возвращает имя
    """
    ip = get_client_ip(request)
    guest = GuestUser.objects.filter(ip_address=ip).order_by('-created_at').first()
    return JsonResponse({"username": guest.username if guest else None})


def get_client_ip(request):
    """
    Получает IP-адрес клиента из заголовков
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    return x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')


def lobby(request):
    """
    Возвращает основную страницу чата или частичный шаблон
    """
    context = get_user_context(request)

    if request.GET.get('partial') == '1':
        return render(request, 'chat/_lobby_partial.html', context)
    return render(request, 'chat/lobby.html', context)


def get_user_context(request):
    """
    Возвращает контекст для отображения комнаты и имени пользователя
    """
    room_names = Room.objects.all().order_by('name').values_list('name', flat=True)

    if request.user.is_authenticated:
        return {
            'username': request.user.username,
            'room_name': '',
            'room_names': room_names,
            'master': True
        }

    ip = get_client_ip(request)
    guest = GuestUser.objects.filter(ip_address=ip).order_by('-created_at').first()

    return {
        'username': guest.username if guest else '',
        'room_name': guest.room.name if guest and guest.room else '',
        'room_names': room_names
    }

