from django.db import models
from cloudinary.models import CloudinaryField
from django.urls import reverse

# 🔹 Модель для проектов
class Project(models.Model):
    title = models.CharField(max_length=200, verbose_name="Название проекта")
    slug = models.SlugField(unique=True)
    description = models.TextField(verbose_name="Описание проекта")
    tech_stack = models.CharField(max_length=255, verbose_name="Используемые технологии")  # Например: Django, React, PostgreSQL
    repo_link = models.URLField(blank=True, null=True, verbose_name="Ссылка на репозиторий")
    demo_link = models.URLField(blank=True, null=True, verbose_name="Ссылка на демо")
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
    created_at = models.DateTimeField(auto_now_add=True)
    image = CloudinaryField('image', blank=True, null=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('')




# 🔹 Модель для контактов (например, чтобы люди могли отправлять сообщения)
class ContactMessage(models.Model):
    name = models.CharField(max_length=100, verbose_name="Имя")
    email = models.EmailField(verbose_name="Email")
    message = models.TextField(verbose_name="Сообщение", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Сообщение от {self.name} ({self.email})"

