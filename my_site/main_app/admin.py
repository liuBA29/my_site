from django.contrib import admin
from .models import *

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}
    # pass

@admin.register(UsefulSoftware)
class UsefulSoftwareAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    # pass


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    pass

