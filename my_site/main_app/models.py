# main_app/models.py

from django.db import models
from cloudinary.models import CloudinaryField
from django.urls import reverse




from django.db import models

class PageView(models.Model):
    path = models.CharField(max_length=255, unique=True)
    views_count = models.PositiveIntegerField(default=0)
    last_viewed = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.path} — {self.views_count} просмотров"


class PageVisitLog(models.Model):
    path = models.CharField(max_length=255)
    viewed_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField()

    def __str__(self):
        return f"{self.viewed_at} - {self.path} - {self.ip_address}"



# 🔹 Модель для проектов
class Project(models.Model):
    title = models.CharField(max_length=200, verbose_name="Название проекта")
    slug = models.SlugField(unique=True)
    description = models.TextField(verbose_name="Описание проекта")
    tech_stack = models.CharField(max_length=255, verbose_name="Используемые технологии")  # Например: Django, React, PostgreSQL
    repo_link = models.URLField(blank=True, null=True, verbose_name="Ссылка на репозиторий")
    demo_link_ru = models.URLField(blank=True, null=True, verbose_name="Ссылка на демо (ru)")
    demo_link_en = models.URLField(blank=True, null=True, verbose_name="Ссылка на демо (en)")
    image = CloudinaryField('image', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('main_app:project_detail', kwargs={'slug':self.slug})

# 🔹 Модель для полезного софта
class UsefulSoftware(models.Model):
    name = models.CharField(max_length=200, verbose_name="Название софта")
    slug = models.SlugField(unique=True)
    description = models.TextField(verbose_name="Описание")
    download_link = models.URLField(verbose_name="Ссылка на скачивание", blank=True, null=True)
    english_link = models.URLField(verbose_name="English version link", blank=True, null=True)  # Новое поле
    download_link_backup = models.URLField(verbose_name="Резервная ссылка (RU)", blank=True, null=True)
    english_link_backup = models.URLField(verbose_name="Резервная ссылка (EN)", blank=True, null=True)
    author = models.CharField(
        max_length=200,
        default="Liubov Kovaleva @LiuBA29",
        verbose_name="Автор"
    )  # Новое поле
    created_at = models.DateTimeField(auto_now_add=True)
    image = CloudinaryField('image', blank=True, null=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('main_app:useful_soft_detail', kwargs={'slug': self.slug})




# 🔹 Модель для контактов (например, чтобы люди могли отправлять сообщения)
class ContactMessage(models.Model):
    name = models.CharField(max_length=100, verbose_name="Имя")
    email = models.EmailField(verbose_name="Email")
    message = models.TextField(verbose_name="Сообщение", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Сообщение от {self.name} ({self.email})"

