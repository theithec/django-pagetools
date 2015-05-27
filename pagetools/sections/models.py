from django.db import models, DatabaseError
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from pagetools.core.models import PublishableLangModel, PublishableLangManager
from pagetools.core.utils import get_adminadd_url


class PageNodeManager(PublishableLangManager):
    #def get_queryset(self):
    def real(self, **kwargs):
        try:
            ct = ContentType.objects.get_for_model(
                self.model, for_concrete_model=False)
            kwargs['content_type_pk'] = ct.id
        except DatabaseError:
            pass
        return super(PageNodeManager, self).get_queryset(kwargs.pop('request')).filter(**kwargs)


class TypeMixin(models.Model):

    node_choices = ()
    node_type = models.CharField(max_length=128, blank=True)

    def __init__(self, *args, **kwargs):
        super(TypeMixin, self).__init__(*args, **kwargs)
        self._meta.get_field('node_type')._choices = self.node_choices

    class Meta:
        abstract = True


class PageNode(PublishableLangModel):

    title = models.CharField(_('Internal Title'), max_length=512)
    slug = models.SlugField(_('Slug'), max_length=128, unique=True)
    classes = models.CharField('Classes', max_length=512, blank=True, null=True)
    allowed_children_keys = ()
    content_type_pk = models.SmallIntegerField(blank=True)
    in_nodes = models.ManyToManyField("self",
                                      through="PageNodePos",
                                      related_name="positioned_content",
                                      symmetrical=False)

    @classmethod
    def get_adminadd_url(Clz):
        return get_adminadd_url(Clz)

    @classmethod
    def get_classname(Clz):
        return Clz._meta.verbose_name

    def get_real_obj(self, node=None):
        node = node or self
        clz = ContentType.objects.get_for_id(node.content_type_pk)
        return clz.model_class().objects.get(pk=node.pk)

    def get_real_content(self, _content):
        content = self.get_real_obj(_content)
        s =  self.slug + "_" + content.slug
        content.long_slug = s
        return content

    def ordered_content(self, **kwargs):
        o = self.positioned_content.lfilter(**kwargs).order_by('pagenodepos')
        return [self.get_real_content(c) for c in o]

    def __str__(self):
        if self.__class__ == PageNode:
            return self.get_real_obj().__str__()
        return self.title

    def save(self, *args, **kwargs):
        if not self.content_type_pk:
            ct = ContentType.objects.get_for_model(self, for_concrete_model=False)
            self.content_type_pk = ct.pk
        super(PageNode, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return "/#%s" % self.slug

    @classmethod
    def get_contenttype_pk(cls):
        t = ContentType.objects.get_for_model(cls, for_concrete_model=False)
        return t.id

    class Meta:
        verbose_name = _('Node')
        verbose_name_plural = _('Nodes')


class PageNodePos(models.Model):

    position = models.PositiveIntegerField()
    content = models.ForeignKey(PageNode)
    owner  = models.ForeignKey(PageNode, related_name="in_group")

    def __str__(self):
        return "%s:%s:%s" %(self.owner, self.content, self.position)

    class Meta:
        ordering = ['position']
        verbose_name = _('Content Position')
        verbose_name_plural = _('Content Positions')

