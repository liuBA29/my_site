# chat/urls.py

from django.urls import path
from . import views

app_name = "chat"
urlpatterns = [
    path('', views.lobby, name="lobby"),
    path('set-username/', views.set_username, name='set_username'),
]