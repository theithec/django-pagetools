'''
Nested content (e.g. for single pages)
A PageNode is a model which may contains other PageNodes.
Inheritated models with own fields needs concrete inheritance,
otherwise a proxy model is sufficient.
'''
import warnings
import django
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType

from filebrowser.fields import FileBrowseField

from pagetools.core.models import PagelikeModel, PublishableLangManager
from pagetools.core.utils import (get_adminadd_url, get_classname, importer,
                                  choices2field)


class PageNodeManager(PublishableLangManager):
    pass


class TypeMixin(models.Model):
    '''Pagenodes that differs only in their representation may use the same
    model but different node choices.
    The node choice is is part of the template names'''
    node_choices = ()
    node_type = models.CharField(
        max_length=128,
        blank=True
    )

    def __init__(self, *args, **kwargs):
        super(TypeMixin, self).__init__(*args, **kwargs)
        choices2field(self._meta.get_field('node_type'), self.node_choices)

    class Meta:
        abstract = True


class PageNode(PagelikeModel):

    classes = models.CharField(
        'Classes', max_length=512, blank=True, null=True)
    content_type_pk = models.SmallIntegerField(blank=True)
    in_nodes = models.ManyToManyField("self",
                                      through="PageNodePos",
                                      related_name="positioned_content",
                                      symmetrical=False)
    objects = PageNodeManager()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        allowed = getattr(self, 'allowed_children_classes', None)
        if allowed:
            repl = []
            for c in allowed:
                repl.append(importer(c))

            self.__class__.allowed_children_classes = repl

    def get_real_obj(self):
        real = self
        if self.pk:
            clz = ContentType.objects.get_for_id(real.content_type_pk)
            real = clz.model_class().objects.get(pk=real.pk)
        return real

    def get_real_child(self, child):
        real_child = child.get_real_obj()
        s = self.slug + "_" + real_child.slug
        real_child.long_slug = s
        return real_child

    def get_real_content(self, child):
        warnings.warn("deprecated, use get_real_child",
                      DeprecationWarning)

        return self.get_real_child(child)

    def children(self, **kwargs):
        o = self.positioned_content.lfilter(**kwargs).order_by('pagenodepos')
        return [self.get_real_child(c) for c in o]

    def ordered_content(self, **kwargs):
        # warnings.warn("deprecated, use get_real_child",
        #              DeprecationWarning)
        return self.children(**kwargs)

    def get_classname(self):
        o = self.get_real_obj()
        return get_classname(o)

    def __str__(self):
        o = self.get_real_obj()
        return "%s(%s)" % (o.title, get_classname(o))

    def clean(self):
        objs = PageNode.objects.filter(slug=self.slug, lang=self.lang)
        lobjs = len(objs)
        if (lobjs == 1 and objs[0].pk != self.pk) or lobjs > 1:
            raise ValidationError(
                _('The slug "%s" for language "%s" is already taken') % (self.slug, self.lang))
        return super().clean()

    def save(self, *args, **kwargs):
        if not self.content_type_pk:
            ct = ContentType.objects.get_for_model(
                self, for_concrete_model=False)
            self.content_type_pk = ct.pk
        super(PageNode, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("sections:node", args=(self.slug,))

    @classmethod
    def get_contenttype_pk(cls):
        t = ContentType.objects.get_for_model(cls, for_concrete_model=False)
        return t.id

    @classmethod
    def get_adminadd_url(Clz):
        return get_adminadd_url(Clz)

    @classmethod
    def get_classname(Clz):
        return Clz._meta.verbose_name

    class Meta:
        verbose_name = _('Node')
        verbose_name_plural = _('Nodes')


class PageNodePos(models.Model):

    position = models.PositiveIntegerField()
    content = models.ForeignKey(PageNode, on_delete=models.CASCADE)
    owner = models.ForeignKey(PageNode, related_name="in_group", on_delete=models.CASCADE)

    def __str__(self):
        return "%s:%s:%s" % (self.owner, self.content, self.position)

    class Meta:
        ordering = ['position']
        verbose_name = _('Included Content')
        verbose_name_plural = _('Included Content')
