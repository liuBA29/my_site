# chat/admin.py

from django.contrib import admin

from .models import *


@admin.register(GuestUser)
class GuestUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'room_name', 'slug', 'ip_address', 'created_at')
    search_fields = ('username', 'room_name')
    list_filter = ('room_name', 'created_at')
    readonly_fields = ('slug',)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('user', 'room_name', 'content', 'timestamp')
    search_fields = ('content', 'user__username', 'room_name')
    list_filter = ('room_name', 'timestamp')

