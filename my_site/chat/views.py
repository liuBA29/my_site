# chat/views.py

from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.contrib.auth.decorators import login_required
from accounts.models import CustomUser, Room
import json



@login_required
@csrf_exempt
def set_username(request):
    """
    Если пользователь авторизован — просто вернуть имя и список комнат.
    """
    if request.method != "POST":
        return JsonResponse({"error": "Метод не разрешён"}, status=405)

    return JsonResponse({
        "message": "Пользователь аутентифицирован",
        "username": request.user.username,
        "all_rooms": list(Room.objects.all().order_by('name').values_list('name', flat=True))
    })


@login_required
@require_GET
def check_user(request):
    """
    Возвращает имя пользователя, если он авторизован.
    """
    return JsonResponse({"username": request.user.username})


@login_required
def lobby(request):
    """
    Страница чата
    """
    context = get_user_context(request)

    if request.GET.get('partial') == '1':
        return render(request, 'chat/_lobby_partial.html', context)
    return render(request, 'chat/lobby.html', context)


def get_user_context(request):
    room_names = Room.objects.all().order_by('name').values_list('name', flat=True)

    # если пользователь не суперюзер — взять первую комнату, в которую он добавлен
    room = None
    if not request.user.is_superuser:
        room = Room.objects.filter(users=request.user).first()

    return {
        'username': request.user.username,
        'room_name': room.name if room else '',
        'room_names': room_names,
        'master': request.user.is_superuser
    }


