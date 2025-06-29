# accounts/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Room

# Для кастомного пользователя можно расширить UserAdmin
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'is_staff', 'is_active', 'get_rooms')  # добавили get_rooms
    filter_horizontal = ('rooms',)

    def get_rooms(self, obj):
        return ", ".join([room.name for room in obj.rooms.all()])
    get_rooms.short_description = 'Rooms'


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at')
    prepopulated_fields = {'slug': ('name',)}  # Чтобы slug автоматически генерировался из name

