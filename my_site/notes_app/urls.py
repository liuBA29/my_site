from django.urls import path
from .views import *

app_name= "notes"
urlpatterns = [
    path('<slug:slug>/', article_detail, name='article_detail'),  # Главная страница
    # path('', views.main_page, name='home'),  # Главная страница
    # path('notes/', views.NoteListView.as_view(), name='note_list'),  # all notes
    # path('note/<int:pk>/', views.NoteDetailView.as_view(), name='note_detail'),
    # path('note/new/', views.NoteCreateView.as_view(), name='note_create'),  # Добавление заметки
    # path('note/<int:pk>/edit/', views.NoteUpdateView.as_view(), name='note_edit'),  # Редактирование заметки
    # path('note/<int:pk>/delete/', views.NoteDeleteView.as_view(), name='note_delete'),  # Удаление заметки
]
