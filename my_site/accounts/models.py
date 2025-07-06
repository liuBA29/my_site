# accounts/models.py

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify
import unicodedata
from unidecode import unidecode
import re

def custom_slugify(value):
    value = str(value)
    value = unidecode(value)  # ← правильно
    value = re.sub(r'[^\w\s-]', '', value).strip().lower()
    return slugify(value)


class Room(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Если имя не на латинице, преобразуем его
        # (например, "Морковкаroom" → "morkovkaroom")
        self.name = unidecode(self.name).lower().replace(" ", "")  # убираем пробелы, можно кастомизировать

        # Формируем slug на основе уже "латинизированного" name
        if not self.slug:
            base_slug = custom_slugify(self.name)
            slug = base_slug
            counter = 1
            while Room.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class CustomUser(AbstractUser):
    rooms = models.ManyToManyField(Room, related_name='users', blank=True)

    def __str__(self):
        return self.username
