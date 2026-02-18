# main_app/urls.py

from django.urls import path
from .views import *


app_name = "main_app"
urlpatterns = [
    path('', main_page, name='home'),  # Главная страница

    path('free-soft/', free_soft, name='free_soft'),  # Бесплатно
    path('free-soft/<slug:slug>/', free_soft_detail, name='free_soft_detail'),
    path('business-soft/', business_soft, name='business_soft'),  # Продукты для бизнеса
    path('business-soft/<slug:slug>/', business_soft_detail, name='business_soft_detail'),
    path('cooperation/', cooperation, name='cooperation'),  # Сотрудничество
    path('my-projects/', my_projects, name='my_projects'),  # Список проектов (без пункта в меню)
    path('project/<slug:slug>/', project_detail, name='project_detail'),
    path('contact/', contact, name='contact'),  #
    path('requisites/', requisites, name='requisites'),  # Реквизиты
    path('order/', order_request, name='order_request'),  # Страница заказа
    path('page-view/', page_view, name='page_view'),  #
    path('visits-log/', visits_log, name='visits_log'),
    
    # Отслеживание скачиваний
    path('download/<str:file_type>/<slug:slug>/', track_download, name='track_download'),
    # Отслеживание внешних ссылок
    path('link/<str:link_type>/<slug:slug>/', track_link, name='track_link'),
]
