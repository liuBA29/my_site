# accounts/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Room

# Для кастомного пользователя можно расширить UserAdmin
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    # Укажем дополнительные поля для отображения в списке пользователей
    list_display = ('username', 'email', 'is_staff', 'is_active')
    # Чтобы видеть ManyToMany-поле rooms на странице пользователя
    filter_horizontal = ('rooms',)

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at')
    prepopulated_fields = {'slug': ('name',)}  # Чтобы slug автоматически генерировался из name

