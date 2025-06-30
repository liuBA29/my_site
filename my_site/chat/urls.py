# chat/urls.py

from django.urls import path
from .views import *

app_name = "chat"
urlpatterns = [
    path('', lobby, name="lobby"),
    path('check-user/', check_user, name='check_user'),
    path('set-username/', set_username, name='set_username'),

]