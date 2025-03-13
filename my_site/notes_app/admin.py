#notes_app/admin.py

from django.contrib import admin
from modeltranslation.admin import TranslationAdmin
from .models import *



# Register your models here.
@admin.register(Article)
class ArticleAdmin(TranslationAdmin):
    prepopulated_fields = {'slug':('title',)}
