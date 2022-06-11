# pylint: disable=import-outside-toplevel
from typing import Dict

from django.apps import AppConfig
from django.forms import Form


class PagesConfig(AppConfig):
    name = "pagetools.pages"
    includable_forms: Dict[str, Form] = {}

    def ready(self):
        from pagetools.subscriptions.forms import SubscribeForm

        from . import forms

        self.includable_forms = {
            "Contactform": forms.ContactForm,
            "Contactfrom(Captcha)": forms.CaptchaContactForm,
            "SubscribeForm": SubscribeForm,
        }
