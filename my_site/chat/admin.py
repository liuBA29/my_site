from django.contrib import admin
from .models import GuestUser, Message, Room


@admin.register(GuestUser)
class GuestUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'get_room_name', 'slug', 'ip_address', 'created_at')
    search_fields = ('username', 'room__name')
    list_filter = ('room', 'created_at')
    readonly_fields = ('slug',)

    def get_room_name(self, obj):
        return obj.room.name if obj.room else '—'
    get_room_name.short_description = 'Room'


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('user', 'guest_user', 'room', 'short_content', 'timestamp')
    search_fields = ('content', 'user__username', 'guest_user__username', 'room__name')
    list_filter = ('room', 'timestamp')

    def short_content(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    short_content.short_description = 'Content'


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at')
    search_fields = ('name', 'slug')
    list_filter = ('created_at',)
