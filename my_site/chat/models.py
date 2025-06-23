# chat/models.py

from django.db import models

from django.utils import timezone
from django.utils.text import slugify
from django.conf import settings
import unicodedata
import re


def custom_slugify(value):
    # Преобразуем кириллицу в латиницу
    value = str(value)
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value).strip().lower()
    return slugify(value)


class GuestUser(models.Model):
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    username = models.CharField(max_length=100)
    room = models.ForeignKey('Room', on_delete=models.SET_NULL, null=True, blank=True, related_name='guests')
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = custom_slugify(self.username)
            slug = base_slug
            counter = 1
            while GuestUser.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.username} ({self.room.name if self.room else 'без комнаты'})"




class Message(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    guest_user = models.ForeignKey(
        GuestUser,
        null=True, blank=True,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    room = models.ForeignKey('Room', on_delete=models.CASCADE, related_name='messages', blank=True, null=True)
    content = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"[{self.timestamp.strftime('%H:%M:%S')}] {self.get_author_name()}: {self.content[:20]}"

    def get_author_name(self):
        if self.user:
            return self.user.username
        elif self.guest_user:
            return self.guest_user.username
        else:
            return "Аноним"



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
