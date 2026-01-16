from django.contrib import admin
from modeltranslation.admin import TranslationAdmin
from .models import *

# main_app/admin.py



@admin.register(PageView)
class PageViewAdmin(admin.ModelAdmin):
    list_display = ('path', 'views_count', 'last_viewed')
    ordering = ('-last_viewed',)
    search_fields = ('path',)


@admin.register(PageVisitLog)
class PageVisitLogAdmin(admin.ModelAdmin):
    list_display = ('viewed_at', 'path', 'ip_address')
    ordering = ('-viewed_at',)
    search_fields = ('path', 'ip_address')
    list_filter = ('viewed_at',)


@admin.register(ExternalLinkLog)
class ExternalLinkLogAdmin(admin.ModelAdmin):
    list_display = ('clicked_at', 'product_name', 'link_type', 'user_os', 'ip_address')
    ordering = ('-clicked_at',)
    search_fields = ('product_name', 'link_type', 'ip_address', 'user_os')
    list_filter = ('link_type', 'user_os', 'clicked_at')
    readonly_fields = ('clicked_at', 'link_type', 'product_name', 'link_url', 'ip_address', 'user_agent', 'referer', 'user_os')
    fieldsets = (
        ('Основная информация', {
            'fields': ('clicked_at', 'link_type', 'product_name')
        }),
        ('Информация о ссылке', {
            'fields': ('link_url',)
        }),
        ('Информация о пользователе', {
            'fields': ('ip_address', 'user_os', 'user_agent', 'referer')
        }),
    )


@admin.register(DownloadLog)
class DownloadLogAdmin(admin.ModelAdmin):
    list_display = ('downloaded_at', 'product_name', 'file_name', 'file_type', 'user_os', 'ip_address')
    ordering = ('-downloaded_at',)
    search_fields = ('product_name', 'file_name', 'ip_address', 'user_os')
    list_filter = ('file_type', 'user_os', 'downloaded_at')
    readonly_fields = ('downloaded_at', 'product_name', 'file_name', 'file_type', 'download_url', 'ip_address', 'user_agent', 'referer', 'user_os')
    fieldsets = (
        ('Основная информация', {
            'fields': ('downloaded_at', 'product_name', 'file_name', 'file_type')
        }),
        ('Информация о файле', {
            'fields': ('download_url',)
        }),
        ('Информация о пользователе', {
            'fields': ('ip_address', 'user_os', 'user_agent', 'referer')
        }),
    )


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