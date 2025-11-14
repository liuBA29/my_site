from modeltranslation.translator import translator, TranslationOptions, register
from .models import *


@register(Project)
class ProjectTranslationOptions(TranslationOptions):
    fields = ('title', 'description',)
    required_languages = ('en', 'ru')


@register(FreeSoftware)
class FreeSoftwareTranslationOptions(TranslationOptions):
    fields = ('name', 'description',)
    required_languages = ('en', 'ru')

@register(BusinessSoftware)
class BusinessSoftwareTranslationOptions(TranslationOptions):
    fields = ('name', 'description',)
    required_languages = ('en', 'ru')


@register(ContactMessage)
class ContactMessageTranslationOptions(TranslationOptions):
    fields = ('name',)
    required_languages = ('en', 'ru')