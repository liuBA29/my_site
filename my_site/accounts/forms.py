# accounts/forms.py



from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser
from django.utils.translation import gettext_lazy as _
from django.conf import settings



# Форма регистрации — расширяем стандартную UserCreationForm
class CustomUserCreationForm(UserCreationForm):
    username = forms.CharField(
        label=_("Username"),
        error_messages={
            'required': _('Please enter a username'),
        },
        widget=forms.TextInput(attrs={'placeholder': _('Your username 💫')})
    )
    email = forms.EmailField(
        label=_("Email"),
        error_messages={
            'required': _('Please enter your email address'),
            'invalid': _('Enter a valid email address'),
        },
        widget=forms.EmailInput(attrs={
            'placeholder': _('Your email ✉')
        })
    )
    password1 = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput(attrs={'placeholder': _('Password')})
    )
    password2 = forms.CharField(
        label=_("Confirm password"),
        widget=forms.PasswordInput(attrs={'placeholder': _('Repeat password')})
    )
    
    # Cloudflare Turnstile поле (скрытое, проверяется через JavaScript)
    cf_turnstile_response = forms.CharField(
        required=False,
        widget=forms.HiddenInput(),
        label=''
    )

    class Meta:
        model = CustomUser
        fields = ('username', 'email')
    
    def clean_cf_turnstile_response(self):
        """Проверка Cloudflare Turnstile токена"""
        token = self.cleaned_data.get('cf_turnstile_response', '')
        
        # Проверяем токен через API Cloudflare
        import requests
        from django.conf import settings
        
        secret_key = getattr(settings, 'CLOUDFLARE_TURNSTILE_SECRET_KEY', '')
        site_key = getattr(settings, 'CLOUDFLARE_TURNSTILE_SITE_KEY', '')
        
        # Если ключи не настроены, пропускаем проверку (для разработки)
        # Но выводим предупреждение
        if not secret_key or not site_key:
            print("⚠️ WARNING: Cloudflare Turnstile keys not configured! Registration is NOT protected.")
            return token
        
        # Если ключи настроены, но токена нет - ошибка
        if not token:
            print("❌ Turnstile token missing - blocking registration")
            raise forms.ValidationError(_('Please complete the verification.'))
        
        # Получаем IP адрес пользователя для дополнительной проверки
        request = getattr(self, 'request', None)
        remote_ip = None
        if request:
            # Проверяем заголовки прокси
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
        
        # Добавляем IP адрес, если доступен
        if remote_ip:
            data['remoteip'] = remote_ip
        
        try:
            response = requests.post(url, data=data, timeout=10)
            result = response.json()
            
            # Отладочная информация
            print(f"🔍 Cloudflare Turnstile API Response: {result}")
            
            if not result.get('success', False):
                error_codes = result.get('error-codes', [])
                print(f"❌ Turnstile verification failed. Error codes: {error_codes}")
                raise forms.ValidationError(_('Verification failed. Please try again.'))
            
            print(f"✅ Turnstile verification successful!")
            return token
        except requests.RequestException as e:
            # В случае ошибки сети, пропускаем проверку (можно изменить на raise)
            print(f"❌ Ошибка проверки Cloudflare Turnstile: {e}")
            return token

# Форма для логина — расширяем AuthenticationForm, чтобы работала с кастомным пользователем
class CustomAuthenticationForm(AuthenticationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'password')
