from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

# Create your models here.
class Article(models.Model):
    title = models.CharField(verbose_name=_('title'), max_length=55)
    slug = models.SlugField(verbose_name=_('slug'), unique=True)
    text=models.TextField(verbose_name=_('text'),)

    def __str__(self):
        return self.title
    def get_absolute_url(self):
        return reverse('notes:article_detail', kwargs={'slug': self.slug})


class Note(models.Model):
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    content = models.TextField(verbose_name="Содержание")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        # Перенаправление на страницу списка заметок после сохранения
        return reverse('note_list')
