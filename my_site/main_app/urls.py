# urls.py

from django.urls import path
from .views import *


app_name = "main_app"
urlpatterns = [
    path('', main_page, name='home'),  # Главная страница
    path('useful-soft/', useful_soft, name='useful_soft'),  #
    path('useful-soft/<slug:slug>/', useful_soft_detail, name='useful_soft_detail'),
    path('my-projects/', my_projects, name='my_projects'),  #
    path('project/<slug:slug>/', project_detail, name='project_detail'),
    path('contact/', contact, name='contact'),  #
    path('page-view/', page_view, name='page_view'),  #
    path('visits-log/', visits_log, name='visits_log'),
]
