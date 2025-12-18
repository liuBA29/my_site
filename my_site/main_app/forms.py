# main_app/forms.py
from django import forms
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from .models import Order


class OrderForm(forms.ModelForm):
    """Форма для создания заказа (заявки)"""
    
    # Добавим варианты типов услуг для удобства
    SERVICE_CHOICES = [
        ('', 'Выберите тип услуги...'),
        ('Разработка сайта', 'Разработка сайта'),
        ('Разработка софта', 'Разработка софта'),
        ('Доработка проекта', 'Доработка существующего проекта'),
        ('Техническая поддержка', 'Техническая поддержка'),
        ('Консультация', 'Консультация'),
        ('Другое', 'Другое'),
    ]
    
    service_type = forms.ChoiceField(
        choices=SERVICE_CHOICES,
        label="Тип услуги",
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    client_name = forms.CharField(
        max_length=200,
        label="Ваше имя",
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Иван Иванов'
        })
    )
    
    client_email = forms.EmailField(
        label="Email",
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'ivan@example.com'
        })
    )
    
    client_phone = forms.CharField(
        max_length=20,
        label="Телефон",
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+7 (999) 123-45-67'
        })
    )
    
    description = forms.CharField(
        label="Описание задачи",
        required=True,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,
            'placeholder': 'Опишите подробно, что вам нужно...'
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
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Статус всегда будет 'new' для новых заказов, не показываем его в форме
    
    def clean_cf_turnstile_response(self):
        """Проверка Cloudflare Turnstile токена"""
        import requests
        
        token = self.cleaned_data.get('cf_turnstile_response', '')
        
        secret_key = getattr(settings, 'CLOUDFLARE_TURNSTILE_SECRET_KEY', '')
        site_key = getattr(settings, 'CLOUDFLARE_TURNSTILE_SITE_KEY', '')
        
        # Если ключи не настроены, пропускаем проверку (для разработки)
        if not secret_key or not site_key:
            print("⚠️ WARNING: Cloudflare Turnstile keys not configured! Order form is NOT protected.")
            return token
        
        # Если ключи настроены, но токена нет - ошибка
        if not token:
            print("❌ Turnstile token missing - blocking order")
            raise forms.ValidationError(_('Please complete the verification.'))
        
        # Получаем IP адрес пользователя для дополнительной проверки
        request = getattr(self, 'request', None)
        remote_ip = None
        if request:
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                remote_ip = x_forwarded_for.split(',')[0].strip()
            else:
                remote_ip = request.META.get('REMOTE_ADDR')
        
        url = 'https://challenges.cloudflare.com/turnstile/v0/siteverify'
        data = {
            'secret': secret_key,
            'response': token,
        }
        
        if remote_ip:
            data['remoteip'] = remote_ip
        
        try:
            response = requests.post(url, data=data, timeout=10)
            result = response.json()
            
            print(f"🔍 Cloudflare Turnstile API Response: {result}")
            
            if not result.get('success', False):
                error_codes = result.get('error-codes', [])
                print(f"❌ Turnstile verification failed. Error codes: {error_codes}")
                raise forms.ValidationError(_('Verification failed. Please try again.'))
            
            print(f"✅ Turnstile verification successful!")
            return token
        except requests.RequestException as e:
            print(f"❌ Ошибка проверки Cloudflare Turnstile: {e}")
            return token

