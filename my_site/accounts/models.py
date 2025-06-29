# accounts/models.py

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify
import unicodedata
import re

def custom_slugify(value):
    value = str(value)
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value).strip().lower()
    return slugify(value)

class Room(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = custom_slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class CustomUser(AbstractUser):
    rooms = models.ManyToManyField(Room, related_name='users', blank=True)

    def __str__(self):
        return self.username
