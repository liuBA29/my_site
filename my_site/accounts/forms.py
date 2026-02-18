# accounts/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.utils.translation import gettext_lazy as _

from main_app.mixins import TurnstileMixin
from .models import CustomUser


class CustomUserCreationForm(TurnstileMixin, UserCreationForm):
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


# Форма для логина — расширяем AuthenticationForm, чтобы работала с кастомным пользователем
class CustomAuthenticationForm(AuthenticationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'password')
