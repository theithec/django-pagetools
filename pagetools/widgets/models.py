from django.db import models
from django.template.context import Context
from django.contrib.contenttypes.fields import (GenericRelation,
                                                GenericForeignKey)
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _


from pagetools.core.models import LangModel, LangManager
from pagetools.core.utils import get_adminedit_url, importer

from . import settings


class BaseWidget(models.Model):
    title = models.CharField(max_length=128, blank=True)
    name = models.SlugField(_('name'), unique=True)
    adapter = GenericRelation('WidgetInArea')

    def __str__(self):
        return "%s:%s" % (self.name, self.title)

    class Meta:
        abstract = True


class ContentWidget(BaseWidget):
    content = models.TextField(_('Content'))

    def get_title(self):
        return self.title or self.name

    def get_content(self, contextdict):
        return self.content

    class Meta:
        verbose_name = _("Simple Text Widget")
        verbose_name_plural = _("Simple Text Widgets")


class TemplateTagWidget(BaseWidget):
    key_choices = [(k, k) for k in sorted(settings.TEMPLATETAG_WIDGETS.keys())]
    renderclasskey = models.CharField(
        max_length=255,
        choices=key_choices
    )

    def __init__(self, *args, **kwargs):
        super(TemplateTagWidget, self).__init__(*args, **kwargs)
        self.robj = None

    def get_rendererobject(self):
        if not self.robj:
            clzname = settings.TEMPLATETAG_WIDGETS.get(
                self.renderclasskey,
                (None)
            )
            clz = importer(clzname)
            if clz:
                self.robj = clz()
        return self.robj

    def get_title(self):
        return '%s' % self.title

    def get_content(self, contextdict):
        if self.get_rendererobject():
            return self.robj.render(Context(contextdict, True))


class PageType(models.Model):
    name = models.CharField('Name', max_length=128)
    parent = models.ForeignKey('self', blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Pagetype")
        verbose_name_plural = _("Pagetypes")


class PageTypeDescription(LangModel):
    ''' The description is meant to be used for the meta description tag'''
    pagetype = models.ForeignKey(PageType)
    description = models.CharField(
        _('Description'),
        max_length=156,
        help_text='''Description (for Metatag/seo)''', blank=True)

    def __str__(self):
        return "%s/%s" % (self.pagetype, self.lang)

    class Meta:
        verbose_name = _("Pagetype-Description")
        verbose_name_plural = _("Pagetype-Descriptions")
        unique_together = ('pagetype', 'lang',)


class TypeArea(LangModel):

    area = models.CharField(max_length=64, choices=sorted(settings.AREAS))
    type = models.ForeignKey(PageType)
    objects = LangManager()

    def full_clean(self, *args, **kwargs):
        f = TypeArea.objects.filter(
            area=self.area, type=self.type, lang=''
        ).exclude(pk=self.pk)
        if f:
            raise ValidationError({'__all__': ('Language Error',)})
        return super(TypeArea, self).full_clean(*args, **kwargs)

    def __str__(self):
        return "%s_%s%s" % (self.area, self.type,
                            ("_%s" % self.lang if self.lang else ""))

    class Meta:
        unique_together = ('area', 'type', 'lang')
        verbose_name = _("Pagetype-Area")
        verbose_name_plural = _("Pagetype-Areas")


class WidgetInArea(models.Model):
    typearea = models.ForeignKey(TypeArea, related_name="widgets")
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    position = models.PositiveIntegerField()
    enabled = models.BooleanField('enabled', default=False)

    def get_title(self):
        return '%s' % self.content_object.title

    def get_content(self, contextdict):
        return self.content_object.get_content(contextdict)

    def adminedit_url(self):
        co = self.content_object
        h = format_html('<a href="{0}">{1}</a>', get_adminedit_url(co), co)
        return h

    def __str__(self):
        return "%s@%s" % (self.content_object, self.typearea.type)

    class Meta:
        ordering = ['position']
        verbose_name = _("Included widget")
        verbose_name_plural = _("Included widgets")
