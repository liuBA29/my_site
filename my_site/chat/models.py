# chat/models.py

from django.db import models
from cloudinary.models import CloudinaryField
from django.utils import timezone
from django.utils.text import slugify
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
    room_name = models.CharField(max_length=100, blank=True)
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

        # Автоматически задаём room_name как '{slug}_room' если room_name пустой или отличается
        desired_room_name = f"{self.slug}_room"
        if self.room_name != desired_room_name:
            self.room_name = desired_room_name


        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.username} ({self.room_name})"



class Message(models.Model):
    user = models.ForeignKey(GuestUser, on_delete=models.CASCADE, related_name='messages')
    room_name = models.CharField(max_length=100)
    content = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"[{self.timestamp.strftime('%H:%M:%S')}] {self.user.username}: {self.content[:20]}"

