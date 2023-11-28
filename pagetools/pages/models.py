"""Models (mostly) for pages."""
from typing import Dict

from django.apps import apps
from django.core.exceptions import ValidationError
from django.db import models
from django.forms import Form
from django.urls import reverse
from django.utils.html import strip_tags
from django.utils.translation import gettext_lazy as _
from tinymce.models import HTMLField

from pagetools.models import PagelikeModel, PublishableLangManager
from pagetools.widgets.models import PageType

from .validators import validate_emails_str


class IncludedForm(models.Model):
    """Mixin that includes a form

     expects in object::

         includable_forms = {
             "name1": Form1,
             # [...]
         }

         or use the settings from the AppConfig for "pages"

     This items will be available as choices for the
     `included form` field.

    See :class:`pagetools.pages.views.IncludedFormMixin`
    """

    includable_forms: Dict[str, Form] = {}
    included_form = models.CharField(_("Included form"), max_length=255, blank=True, choices=(("dummy", "dummy"),))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        appconf = apps.get_app_config("pages")
        self.__class__.includable_forms = self.__class__.includable_forms or appconf.includable_forms
        choices = [(i, _(i)) for i in self.includable_forms.keys()]
        self._meta.get_field("included_form").choices = choices

    class Meta:
        abstract = True


class IncludedEmailForm(IncludedForm):
    """Included Form with email recevivers field

    The :class:pagetools.pages.views.IncludedFormMixin will add
    `email_receivers_list` to the form kwargs.
    """

    email_receivers = models.CharField(
        _("Email Receivers"),
        max_length=512,
        blank=True,
        help_text="Comma separated list of emails",
    )

    def clean(self):
        super().clean()
        if self.included_form and getattr(self.included_form, "USE_MAILRECEIVERS", False) and not self.email_receivers:
            raise ValidationError(_('''The selected form requires "email_receivers"'''))
        validate_emails_str(self.email_receivers)

    def email_receivers_list(self):
        return [part.strip() for part in self.email_receivers.split(",") if part.strip()]

    class Meta:
        abstract = True


class AuthPage(models.Model):
    """Page with a `login_required` field.

    The ::class::pagetools.pages.views.IncludedFormMixin will add
    `email_receivers_list` to the form kwargs.
    """

    login_required = models.BooleanField(_("Login required"), default=False)

    class Meta:
        abstract = True


class BasePage(IncludedEmailForm, AuthPage, PagelikeModel):
    """A basemodel for a page with one main content area"""

    content = HTMLField(_("Content"))
    objects = models.Manager()
    pagetype = models.ForeignKey(PageType, blank=True, null=True, on_delete=models.CASCADE)

    def get_pagetype(self, **kwargs):
        return self.pagetype

    def get_absolute_url(self):
        return reverse("pages:pageview", kwargs={"slug": self.slug})

    class Meta(PagelikeModel.Meta):
        verbose_name = _("Page")
        verbose_name_plural = _("Pages")
        unique_together = ("slug", "lang")
        abstract = True


class Page(BasePage):
    objects = PublishableLangManager()


class PageBlockMixin(models.Model):
    """Abstract Content blocks for pages"""

    content = HTMLField(_("Content"), blank=True)
    visible = models.BooleanField(_("Visible"), default=True)
    # in concrete model:
    # page = models.ForeignKey(MyBlockPage)
    position = models.PositiveIntegerField()

    class Meta:
        verbose_name = "Block"
        ordering = ("position",)
        abstract = True

    def __str__(self):
        content_len = len(self.content)
        stripped = strip_tags(self.content) or self.content
        return stripped[: 100 if content_len > 100 else content_len]
