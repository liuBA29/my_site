# chat/urls.py

from django.urls import path
from .views import *

app_name = "chat"
urlpatterns = [
    path('', lobby, name="lobby"),
    path('set-username/', set_username, name='set_username'),
]