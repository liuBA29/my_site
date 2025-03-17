from django.contrib import admin
from modeltranslation.admin import TranslationAdmin
from .models import *

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

