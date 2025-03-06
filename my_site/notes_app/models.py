from django.db import models
from django.urls import reverse

# Create your models here.
class Note(models.Model):
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    content = models.TextField(verbose_name="Содержание")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        # Перенаправление на страницу списка заметок после сохранения
        return reverse('note_list')
