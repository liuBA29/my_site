# main_app/mixins.py
"""
Общая логика проверки Cloudflare Turnstile для форм (заказ, регистрация).
"""
import logging

import requests
from django import forms
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from .utils import get_client_ip

logger = logging.getLogger(__name__)

TURNSTILE_VERIFY_URL = "https://challenges.cloudflare.com/turnstile/v0/siteverify"


class TurnstileMixin:
    """
    Mixin для форм с полем cf_turnstile_response.
    Добавляет clean_cf_turnstile_response(): проверка токена через API Cloudflare.
    У формы должен быть атрибут request (опционально), чтобы передать IP в API.
    """

    def clean_cf_turnstile_response(self):
        token = self.cleaned_data.get("cf_turnstile_response", "")
        secret_key = getattr(settings, "CLOUDFLARE_TURNSTILE_SECRET_KEY", "")
        site_key = getattr(settings, "CLOUDFLARE_TURNSTILE_SITE_KEY", "")

        if not secret_key or not site_key:
            logger.warning(
                "Cloudflare Turnstile keys not configured! Form is NOT protected."
            )
            return token

        if not token:
            logger.warning("Turnstile token missing - blocking submit")
            raise forms.ValidationError(_("Please complete the verification."))

        request_obj = getattr(self, "request", None)
        remote_ip = get_client_ip(request_obj) if request_obj else None

        data = {"secret": secret_key, "response": token}
        if remote_ip:
            data["remoteip"] = remote_ip

        try:
            response = requests.post(TURNSTILE_VERIFY_URL, data=data, timeout=10)
            result = response.json()
            logger.debug("Cloudflare Turnstile API Response: %s", result)

            if not result.get("success", False):
                error_codes = result.get("error-codes", [])
                logger.warning("Turnstile verification failed. Error codes: %s", error_codes)
                raise forms.ValidationError(_("Verification failed. Please try again."))
            return token
        except requests.RequestException:
            logger.exception("Ошибка проверки Cloudflare Turnstile")
            return token
