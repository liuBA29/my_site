
# chat/admin.py

from django.contrib import admin
from .models import Message



@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('user', 'room', 'content', 'timestamp')
    search_fields = ('user__username', 'room__name', 'content')
    list_filter = ('room', 'timestamp')
    ordering = ('-timestamp',)



