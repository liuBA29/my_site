# main_app/urls.py

from django.urls import path
from .views import *


app_name = "main_app"
urlpatterns = [
    path('', main_page, name='home'),  # Главная страница

    path('free-soft/', free_soft, name='free_soft'),  # Бесплатный софт
    path('free-soft/<slug:slug>/', free_soft_detail, name='free_soft_detail'),
    path('business-soft/', business_soft, name='business_soft'),  # Софт для бизнеса
    path('business-soft/<slug:slug>/', business_soft_detail, name='business_soft_detail'),
    path('my-projects/', my_projects, name='my_projects'),  #
    path('project/<slug:slug>/', project_detail, name='project_detail'),
    path('contact/', contact, name='contact'),  #
    path('order/', order_request, name='order_request'),  # Страница заказа
    path('page-view/', page_view, name='page_view'),  #
    path('visits-log/', visits_log, name='visits_log'),
]
