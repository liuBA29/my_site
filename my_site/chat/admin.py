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
    list_display = ('user', 'guest_user', 'room', 'content', 'timestamp')

    search_fields = ('content', 'user__guest_user', 'room_name')
    list_filter = ('room', 'timestamp')


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at')
    search_fields = ('name', 'slug', 'created_at')
    list_filter = ('name', 'slug')
