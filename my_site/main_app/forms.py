# main_app/forms.py
from django import forms
from django.utils.translation import gettext_lazy as _

from .mixins import TurnstileMixin
from .models import Order


class OrderForm(TurnstileMixin, forms.ModelForm):
    """Форма для создания заказа (заявки)"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Статус всегда будет 'new' для новых заказов, не показываем его в форме
        # Динамически создаём choices для поддержки переводов
        # Используем ключи на английском для сохранения в БД, но показываем переводы
        self.fields['service_type'].choices = [
            ('', _('Select service type...')),
            ('Website development', _('Website development')),
            ('Software development', _('Software development')),
            ('Project modification', _('Existing project modification')),
            ('Technical support', _('Technical support')),
            ('Consultation', _('Consultation')),
            ('Other', _('Other')),
        ]
    
    service_type = forms.ChoiceField(
        choices=[],  # Будет заполнено в __init__
        label=_("Service type"),
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    client_name = forms.CharField(
        max_length=200,
        label=_("Your name"),
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('John Doe')
        })
    )
    
    client_email = forms.EmailField(
        label=_("Email"),
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'john@example.com'
        })
    )
    
    client_phone = forms.CharField(
        max_length=20,
        label=_("Phone"),
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+1 (555) 123-45-67'
        })
    )
    
    description = forms.CharField(
        label=_("Task description"),
        required=True,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,
            'placeholder': _('Please describe in detail what you need...')
        })
    )
    
    # Cloudflare Turnstile поле (скрытое, проверяется через JavaScript)
    cf_turnstile_response = forms.CharField(
        required=False,
        widget=forms.HiddenInput(),
        label=''
    )
    
    class Meta:
        model = Order
        fields = ['client_name', 'client_email', 'client_phone', 'service_type', 'description']

