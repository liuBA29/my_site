#notes_app/admin.py

from django.contrib import admin
from .models import *



# Register your models here.
@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug':('title',)}
