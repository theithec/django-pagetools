"""
Nested content (e.g. for single pages)
A PageNode is a model which may contains other PageNodes.
Inheritated models with own fields needs concrete inheritance,
otherwise a proxy model is sufficient.
"""
from typing import Iterable, List, Tuple, Type, Union

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from pagetools.models import PagelikeModel, PublishableLangManager
from pagetools.utils import get_adminadd_url, get_classname, importer


class PageNodeManager(PublishableLangManager):
    pass


class TypeMixin(models.Model):
    """Pagenodes that differs only in their representation may use the same
    model but different node choices.
    The node choice is is part of the template names"""

    node_choices: Iterable[Tuple[str, str]] = ()
    node_type = models.CharField(max_length=128, blank=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._meta.get_field("node_type").choices = self.node_choices

    class Meta:
        abstract = True


class PageNode(PagelikeModel):

    classes = models.CharField("Classes", max_length=512, blank=True, null=True)
    content_type_pk = models.ForeignKey(
        ContentType,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        db_column="content_type_pk",
    )
    content_object = GenericForeignKey("content_type_pk", "id")
    in_nodes = models.ManyToManyField(
        "self",
        through="PageNodePos",
        related_name="positioned_content",
        symmetrical=False,
    )
    objects = PageNodeManager()
    allowed_children_classes: List[Union[str, Type[models.Model]]] = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        allowed = getattr(self, "allowed_children_classes", None)
        if allowed:
            repl = []
            for cls in allowed:
                repl.append(importer(cls))

            self.__class__.allowed_children_classes = repl
        self.real_obj = None

    def get_real_obj(self):
        return self.content_object or self

    # def get_real_child(self, child):
    #     real_child = child.get_real_obj()
    #     slug = self.slug + "_" + real_child.slug
    #     real_child.long_slug = slug
    #     return real_child

    def children_queryset(self, **kwargs):
        queryset = self.positioned_content.lfilter(**kwargs).prefetch_related("content_object").order_by("pagenodepos")
        return queryset

    def children(self, **_kwargs):
        queryset = self.children_queryset()
        return [child.get_real_obj() for child in queryset]

    def ordered_content(self, **kwargs):
        return self.children(**kwargs)

    def get_classname(self):
        obj = self.get_real_obj()
        return get_classname(obj)

    def __str__(self):
        return f"{self.title}({self.get_classname()})"

    def clean(self):
        objs = PageNode.objects.filter(slug=self.slug, lang=self.lang)
        lobjs = len(objs)
        if (lobjs == 1 and objs[0].pk != self.pk) or lobjs > 1:
            raise ValidationError(_('The slug "%s" for language "%s" is already taken') % (self.slug, self.lang))
        return super().clean()

    def save(self, *args, **kwargs):
        if self.__class__.__name__ != "PageNode":
            ctype = ContentType.objects.get_for_model(self.__class__, for_concrete_model=False)
            self.content_type_pk = ctype
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("sections:node", args=(self.slug,))

    @classmethod
    def get_contenttype_pk(cls):
        ctype = ContentType.objects.get_for_model(cls, for_concrete_model=False)
        return ctype.id

    @classmethod
    def get_adminadd_url(cls):
        return get_adminadd_url(cls)

    class Meta:
        verbose_name = _("Node")
        verbose_name_plural = _("Nodes")


class PageNodePos(models.Model):

    position = models.PositiveIntegerField()
    content = models.ForeignKey(PageNode, on_delete=models.CASCADE)
    owner = models.ForeignKey(PageNode, related_name="in_group", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.owner}:{self.content}:{self.position}"

    class Meta:
        ordering = ["position"]
        verbose_name = _("Included Content")
        verbose_name_plural = _("Included Content")
