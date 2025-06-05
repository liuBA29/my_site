# chat/views.py

from django.shortcuts import render

def lobby(request):
    username = request.user.username if request.user.is_authenticated else ''
    return render (request, 'chat/lobby.html', {'username': username})