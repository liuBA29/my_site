# chat/models.py

from django.db import models
from cloudinary.models import CloudinaryField
from django.utils import timezone


class GuestUser(models.Model):
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    username = models.CharField(max_length=100)
    room_name = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.username} ({self.room_name})"


class Message(models.Model):
    user = models.ForeignKey(GuestUser, on_delete=models.CASCADE, related_name='messages')
    room_name = models.CharField(max_length=100)
    content = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"[{self.timestamp.strftime('%H:%M:%S')}] {self.user.username}: {self.content[:20]}"

