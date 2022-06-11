from django import template
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from pagetools.models import LangManager, LangModel
from pagetools.utils import get_adminedit_url, importer

from . import settings


class BaseWidget(models.Model):
    template_name = "widgets/basewidget.html"
    title = models.CharField(max_length=128, blank=True)
    name = models.SlugField(_("name"), unique=True)
    adapter = GenericRelation("widgets.WidgetInArea")

    def get_title(self, context):  # pylint: disable=unused-argument
        return self.title

    def get_template_name(self, context):  # pylint: disable=unused-argument
        return self.template_name

    def render(self, context, request):
        templ = template.loader.get_template(self.get_template_name(context))
        context["title"] = self.get_title(context)
        context["content"] = self.get_content(context, request)
        return mark_safe(templ.render(context, request=request))

    def get_content(self, context, request):  # pylint: disable=unused-argument
        raise NotImplementedError()

    def __str__(self):
        return "%s:%s" % (self.name, self.title)

    class Meta:
        abstract = True


class ContentWidget(BaseWidget):
    """
    A wiget with a text area
    """

    content = models.TextField(_("Content"))

    def get_content(self, context, request):  # pylint: disable=unused-argument
        return self.content

    class Meta:
        verbose_name = _("Simple Text Widget")
        verbose_name_plural = _("Simple Text Widgets")


class TemplateTagWidget(BaseWidget):
    """
    Renders a TemplateTag
    """

    key_choices = [(key, key) for key in sorted(settings.TEMPLATETAG_WIDGETS.keys())]
    renderclasskey = models.CharField(max_length=255, choices=key_choices)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.templatetag_instance = None

    def load_templatetag_instance(self):
        """Set the TemplateTag-like instance"""
        if not self.templatetag_instance:
            clzname = settings.TEMPLATETAG_WIDGETS.get(self.renderclasskey, (None))
            clz = importer(clzname)
            if clz:
                self.templatetag_instance = clz()
        return self.templatetag_instance

    def get_content(self, context, request):
        if self.load_templatetag_instance():
            context["request"] = request
            return self.templatetag_instance.render(context)

        return None


class PageType(models.Model):
    """A key that defines which additional context should be added to the context."""

    name = models.CharField("Name", max_length=128)
    parent = models.ForeignKey("self", blank=True, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Pagetype")
        verbose_name_plural = _("Pagetypes")


class TypeArea(LangModel):
    """An area associated with a `PageType`"""

    area = models.CharField(max_length=64, choices=sorted(settings.AREAS))
    pagetype = models.ForeignKey(PageType, on_delete=models.CASCADE)
    objects = LangManager()

    def clean(self, *args, **kwargs):
        super().clean(*args, **kwargs)
        filtered = TypeArea.objects.filter(area=self.area, pagetype=self.pagetype, lang="").exclude(pk=self.pk)
        if filtered:
            raise ValidationError({"__all__": ("Language Error",)})

    def __str__(self):
        return "%s_%s%s" % (
            self.area,
            self.pagetype,
            ("_%s" % self.lang if self.lang else ""),
        )

    class Meta:
        unique_together = ("area", "pagetype", "lang")
        verbose_name = _("Pagetype-Area")
        verbose_name_plural = _("Pagetype-Areas")


class WidgetInArea(models.Model):
    """A widget associated with an area"""

    typearea = models.ForeignKey(TypeArea, related_name="widgets", on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")
    position = models.PositiveIntegerField()
    enabled = models.BooleanField("enabled", default=False)

    def get_title(self):
        return "%s" % self.content_object.title

    def get_content(self, contextdict, request):
        return self.content_object.render(contextdict, request)

    def adminedit_url(self):
        obj = self.content_object
        return format_html('<a href="{0}">{1}</a>', get_adminedit_url(obj), obj)

    def __str__(self):
        return "%s@%s" % (self.content_object, self.typearea.pagetype)

    class Meta:
        ordering = ["position"]
        verbose_name = _("Included widget")
        verbose_name_plural = _("Included widgets")
