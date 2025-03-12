from modeltranslation.translator import translator, TranslationOptions, register
from .models import Article


@register(Article)
class ArticleTranslationOptions(TranslationOptions):
    fields = ('title', 'text',)
    required_languages = ('en', 'ru')