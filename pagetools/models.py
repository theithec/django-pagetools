"""Core models for pagetools
"""

import warnings

from django.conf import settings
from django.db import models
from django.utils.translation import get_language
from django.utils.translation import gettext_lazy as _
from model_utils.choices import Choices
from model_utils.models import StatusModel, TimeStampedModel

from . import settings as ptsettings


class LangManager(models.Manager):
    """
    Manager for models with a lang-field
    """

    def __init__(self, *args, **kwargs):
        super(LangManager, self).__init__(*args, **kwargs)
        self.use_lang = bool(getattr(settings, "LANGUAGES", False))

    def lfilter(self, lang=False, **kwargs):
        """Uses keyword-argument or system-language to add 'lang' to filter-
        arguments if settings.LANGUAGES compares not to null"""

        if self.use_lang and not kwargs.pop("skip_lang", False):
            if lang is False:
                lang = get_language() or ""
            kwargs.update(lang__in=(lang, lang.split("-")[0], ""))
        return self.filter(**kwargs)


class LangModel(models.Model):
    """
    Model with a ``lang``-field.

    Note:
        To avoid `NOT NULL constraint failed` errors,
        empty lang is saved as "".
    """

    objects = models.Manager()
    # public = LangManager()
    lang = models.CharField(
        max_length=20,
        choices=settings.LANGUAGES,
        blank=True,
        verbose_name=_("language"),
    )

    def save(self, *args, **kwargs):
        if self.lang is None:
            self.lang = ""
        super(LangModel, self).save(*args, **kwargs)

    class Meta:
        abstract = True


class PublishableLangManager(LangManager):
    """
    Manager that finds published content language filtered
    """

    def lfilter(self, **kwargs):
        """
        For non authenticated users returns only published content
        and filters for language (if settings.LANGUAGES has entries)
        See :class: `LangManager`
        """

        user = kwargs.pop("user", None)
        if not user or not user.is_authenticated:
            kwargs["status"] = ptsettings.STATUS_PUBLISHED
        return LangManager.lfilter(self, **kwargs)


class PublishableLangModel(LangModel, StatusModel):
    """
    Model with a language and a status field and a ``PublishableLangManager``
    """

    _translated_choices = [(slug, _(name)) for (slug, name) in ptsettings.STATUS_CHOICES]
    STATUS = Choices(*_translated_choices)
    public = PublishableLangManager()

    def _enabled(self):
        warnings.warn("Depricated. Bad naming. Use ``is_published``.")
        return self.status == ptsettings.STATUS_PUBLISHED

    _enabled.boolean = True  # type: ignore
    _enabled.admin_order_field = "status"  # type: ignore
    enabled = property(_enabled)

    def _is_published(self):
        return self.status == ptsettings.STATUS_PUBLISHED

    _is_published.boolean = True  # type: ignore
    _is_published.admin_order_field = "status"  # type: ignore
    is_published = property(_is_published)

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

    def get_absolute_url(self):
        """Dummy"""
        return "/%s" % self.slug

    def __str__(self):
        return self.title

    class Meta:
        abstract = True
