"""Core models, managers and querysets for pagetools
"""

# pylint: disable=arguments-differ  # because of kwargs
from typing import Any, ClassVar, Protocol

from django.conf import settings
from django.db import models
from django.utils.translation import get_language
from django.utils.translation import gettext_lazy as _
from django_stubs_ext import StrOrPromise
from model_utils.choices import Choices
from model_utils.models import StatusModel, TimeStampedModel

from . import settings as ptsettings


class AdminAttributes(Protocol):
    short_description: StrOrPromise
    allow_tags: bool
    boolean: bool
    admin_order_field: str


def admin_attr_decorator(func: Any) -> AdminAttributes:
    return func


class LangQueryset(models.QuerySet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.use_lang = bool(getattr(settings, "LANGUAGES", False))

    def lfilter(self, lang=False, **kwargs):
        """Uses keyword-argument or system-language to add 'lang' to filter-
        arguments if settings.LANGUAGES compares not to null"""

        if self.use_lang and not kwargs.pop("skip_lang", False):
            if lang is False:
                lang = get_language() or ""
            assert isinstance(lang, str)
            kwargs.update(lang__in=(lang, lang.split("-")[0], ""))
        return self.filter(**kwargs)


class LangManager(models.Manager):
    """
    Manager for models with a lang-field
    """

    def get_queryset(self):
        return LangQueryset(self.model, using=self._db)

    def lfilter(self, lang=False, **kwargs):
        return self.get_queryset().lfilter(lang=lang, **kwargs)


class LangModel(models.Model):
    """
    Model with a ``lang``-field.

    Note:
        To avoid `NOT NULL constraint failed` errors,
        empty lang is saved as "".
    """

    objects: ClassVar[models.Manager] = models.Manager()
    lang = models.CharField(
        max_length=20,
        choices=settings.LANGUAGES,
        blank=True,
        verbose_name=_("language"),
    )

    def save(self, *args, **kwargs):
        if self.lang is None:
            self.lang = ""
        super().save(*args, **kwargs)

    class Meta:
        abstract = True


class PublishableQueryset(LangQueryset):
    def lfilter(self, **kwargs):
        """
        For non authenticated users returns only published content
        """
        user = kwargs.pop("user", None)
        if not user or not user.is_authenticated:
            kwargs["status"] = ptsettings.STATUS_PUBLISHED
        return LangQueryset.lfilter(self, **kwargs)


class PublishableLangQueryset(LangQueryset):
    def lfilter(self, **kwargs):
        """
        For non authenticated users returns only published content
        and filters for language (if settings.LANGUAGES has entries)
        See :class: `LangManager`
        """

        user = kwargs.pop("user", None)
        if not user or not user.is_authenticated:
            kwargs["status"] = ptsettings.STATUS_PUBLISHED
        return LangQueryset.lfilter(self, **kwargs)


class PublishableLangManager(LangManager):
    """
    Manager that finds published content language filtered
    """

    def get_queryset(self):
        return PublishableLangQueryset(self.model, using=self._db)


class PublishableLangModel(LangModel, StatusModel):
    """
    Model with a language and a status field and a ``PublishableLangManager``
    """

    _translated_choices = [(slug, _(name)) for (slug, name) in ptsettings.STATUS_CHOICES]
    STATUS = Choices(*_translated_choices)
    public: ClassVar[PublishableLangManager] = PublishableLangManager()

    @admin_attr_decorator
    def _is_published(self):
        return self.status == ptsettings.STATUS_PUBLISHED

    _is_published.boolean = True
    _is_published.admin_order_field = "status"
    is_published = property(_is_published)  # type: ignore

    class Meta:
        abstract = True


class PagelikeModel(TimeStampedModel, PublishableLangModel):
    """
    This could be a base model for everything that inclines a detail_view

    Args:
        title (str)
        slug (str)
        description (Optional[str]): for metatag/seo
    """

    title = models.CharField(_("Title"), max_length=255)
    slug = models.SlugField(_("Slug"), max_length=255, allow_unicode=True)
    description = models.CharField(
        _("Description"),
        max_length=156,
        help_text="""Description (for searchengines)""",
        blank=True,
    )

    def get_absolute_url(self) -> str:
        """Dummy"""
        return f"/{self.slug}"

    def __str__(self) -> str:
        return str(self.title)

    class Meta:
        abstract = True
