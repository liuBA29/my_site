# chat/views.py

from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json

@csrf_exempt
def set_username(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        request.session['username'] = data.get('username', '')
        return JsonResponse({'status': 'ok'})
    elif request.method == 'GET':
        username = request.session.get('username', '')
        return JsonResponse({'username': username})





def lobby(request):
    if request.user.is_authenticated:
        username = request.user.username  # для зарегистрированных
    else:
        username = request.session.get('username', '')  # для гостей

    return render(request, 'chat/lobby.html', {'username': username})
