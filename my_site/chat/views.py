# chat/views.py

from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import GuestUser
import json


@csrf_exempt
def set_username(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username', '').strip()
        room_name = data.get('room_name', '').strip()

        request.session['username'] = username
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
    if request.GET.get('partial') == '1':
        context = get_user_context(request)
        return render(request, 'chat/_lobby_partial.html', context)

    context = get_user_context(request)
    return render(request, 'chat/lobby.html', context)


def get_user_context(request):
    if request.user.is_authenticated:
        return {
            'username': request.user.username,
            'room_name': '',
        }
    else:
        ip = get_client_ip(request)
        guest = GuestUser.objects.filter(ip_address=ip).order_by('-created_at').first()

        if guest:
            request.session['username'] = guest.username
            return {
                'username': guest.username,
                'room_name': guest.room_name,
            }
        else:
            return {
                'username': '',
                'room_name': '',
            }
