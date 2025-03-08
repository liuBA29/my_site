from django.urls import path
from . import views

urlpatterns = [
    path('', views.main_page, name='home'),  # Главная страница
    path('useful-soft/', views.useful_soft, name='useful_soft'),  #
    # path('note/<int:pk>/', views.NoteDetailView.as_view(), name='note_detail'),
    path('my-projects/', views.my_projects, name='my_projects'),  #
    path('contact/', views.contact, name='contact'),  #
    # path('note/<int:pk>/delete/', views.NoteDeleteView.as_view(), name='note_delete'),  # Удаление заметки
]
