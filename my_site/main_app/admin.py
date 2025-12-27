from django.contrib import admin
from modeltranslation.admin import TranslationAdmin
from .models import *

# main_app/admin.py



@admin.register(PageView)
class PageViewAdmin(admin.ModelAdmin):
    list_display = ('path', 'views_count', 'last_viewed')
    ordering = ('-last_viewed',)
    search_fields = ('path',)


@admin.register(Project)
class ProjectAdmin(TranslationAdmin):
    prepopulated_fields = {'slug': ('title',)}
    # pass

@admin.register(FreeSoftware)
class FreeSoftwareAdmin(TranslationAdmin):
    prepopulated_fields = {'slug': ('name',)}
    # pass

@admin.register(BusinessSoftware)
class BusinessSoftwareAdmin(TranslationAdmin):
    prepopulated_fields = {'slug': ('name',)}
    # pass


@admin.register(ContactMessage)
class ContactMessageAdmin(TranslationAdmin):
    pass


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('client_name', 'client_email', 'service_type', 'product_name', 'status', 'ip_address', 'created_at')
    list_filter = ('status', 'created_at', 'service_type')
    search_fields = ('client_name', 'client_email', 'description', 'ip_address', 'product_name')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Основная информация', {
            'fields': ('status', 'created_at', 'updated_at')
        }),
        ('Данные клиента', {
            'fields': ('client_name', 'client_email', 'client_phone', 'ip_address')
        }),
        ('Информация о заказе', {
            'fields': ('service_type', 'description')
        }),
        ('Информация о продукте', {
            'fields': ('product_name', 'product_version', 'product_price'),
            'classes': ('collapse',)
        }),
    )
    ordering = ('-created_at',)  # Новые заказы сначала