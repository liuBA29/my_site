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

@admin.register(UsefulSoftware)
class UsefulSoftwareAdmin(TranslationAdmin):
    prepopulated_fields = {'slug': ('name',)}
    # pass


@admin.register(ContactMessage)
class ContactMessageAdmin(TranslationAdmin):
    pass

