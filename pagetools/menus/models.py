from collections import defaultdict
import logging
import django
from django import template
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models.signals import pre_delete
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _

from mptt.fields import TreeForeignKey
from mptt.managers import TreeManager
from mptt.models import MPTTModel

from pagetools.core.models import LangManager, LangModel
from pagetools.core.utils import get_classname, get_adminedit_url

import pagetools.menus.utils
from .settings import MENU_TEMPLATE
from .apps import MenusConfig

logger = logging.getLogger("pagetools")


class MenuEntryManager(TreeManager, LangManager):

    def add_child(self, content_object, **kwargs):
        if not getattr(content_object, 'get_absolute_url', None):
            raise ValidationError(
                _('MenuEntry.content_object requires get_absolute_url'))
        kwargs['title'] = kwargs.get('title', '%s' % content_object)
        kwargs['content_type'] = ContentType.objects.get_for_model(
            content_object, for_concrete_model=False)
        kwargs['object_id'] = content_object.pk
        kwargs['slug'] = '%s' % getattr(
            content_object, 'slug',
            slugify(content_object))
        try:
            created = False
            entry, created = self.get_or_create(**kwargs)
        except KeyError:
            pass
        if not created:
            raise ValidationError(
                _('Entry %(title)s already exists in %(parent)s'),
                params=kwargs)
        return entry


class MenuManager(MenuEntryManager):

    def create(self, *args, **kwargs):
        raise AttributeError(
            _("Use 'add_child' or 'add_root' instead of 'create'"))

    def add_root(self, title, **kwargs):
        menu, created = TreeManager.get_or_create(
            self,
            title=title,
            parent=None,
            **kwargs
        )
        if not created:
            raise ValidationError(
                _('Menu %(name)s already exists'),
                params={'name': title}
            )
        return menu


class MenuEntry(MPTTModel, LangModel):
    title = models.CharField(_('Title'), max_length=128)
    slug = models.CharField(
        _('slug'), max_length=512,
        help_text=(_('Slug')),
        default='', blank=True)
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', on_delete=models.CASCADE)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    enabled = models.BooleanField(default=False)
    objects = MenuEntryManager()

    def get_entry_classname(self):
        return get_classname(self.content_object.__class__)

    def __str__(self):
        return '%s%s' % (
            self.title, (' (%s)' % self.lang) if self.lang else '')

    def get_absolute_url(self):
        return self.content_object.get_absolute_url()

    def clean(self):
        kwargs = {
            'title': self.title,
            'lang': self.lang,
            # 'parent__is_null=True
        }
        if not self.parent:  # root
            kwargs['parent__isnull'] = True

        entries = MenuEntry.objects.filter(**kwargs)
        if self.parent:  # not root
            root = self.parent.get_root()
            if entries:
                for entry in entries:
                    is_same = self.pk and self.pk == entry.pk
                    if not is_same and entry.get_root() == root:
                        raise ValidationError(
                            _('An entry with this title and language already exists in menu'))
            else:  # root
                if entries:
                    raise ValidationError(
                        _('A menu with this title and language already exists'))

    class Meta:
        pass


def delete_content(sender, **kwargs):
    try:
        object_id = int(kwargs['instance'].pk)
    except ValueError:
        return

    entries = MenuEntry.objects.filter(
        content_type=ContentType.objects.get_for_model(sender),
        object_id=object_id)
    if entries:
        entries.delete()


pre_delete.connect(delete_content)


class SelectedEntries(defaultdict):
    def __missing__(self, key):
        return ''


class MenuCache(models.Model):
    menu = models.OneToOneField('Menu', blank=True, null=True, on_delete=models.CASCADE)
    cache = models.TextField()

    def __str__(self):
        return 'Cache: %s' % self.menu

    def get_absolute_url(self):
        return ""


class Menu(MenuEntry):
    objects = MenuManager()

    def _render_no_sel(self):
        tmpl = template.loader.get_template(MENU_TEMPLATE)
        children = self.children_list()
        return tmpl.render({'children': children, })

    def render(self, selected):
        sel_entries = SelectedEntries()
        for sel in selected:
            sel_entries['sel_' + sel] = 'active'
        use_cache = self.enabled
        tmplstr = None
        if use_cache:
            tmplstr = MenuCache.objects.get(menu=self).cache
        else:
            tmplstr = self._render_no_sel()
        logger.debug(
            " TEMPLATE %s,  SELECTED: %s, KEYS: %s",
            tmplstr, selected, ", ".join(sel_entries.keys()))
        rendered = tmplstr % sel_entries
        return rendered

    def update_entries(self, orderstr):
        '''orderstr = jquery.mjs.nestedSortable.js / serialize()'''
        entry_strs = orderstr.split("&")
        parent = None
        for entry_str in entry_strs:
            if not entry_str:
                break
            key, parent_id = entry_str.split("=")
            br1, br2 = list(map(key.find, ("[", "]")))
            entry_id = int(entry_str[br1 + 1: br2])
            entry = MenuEntry.objects.get(id=entry_id)
            try:
                parent = MenuEntry.objects.get(id=int(parent_id))
            except ValueError:
                parent = entry.get_root()
            entry.move_to(parent, 'last-child')
            entry = MenuEntry.objects.get(pk=entry.pk)
        MenuEntry.objects.rebuild()
        self.save()

    def full_clean(self, *args, **kwargs):
        found = Menu.objects.filter(
            title=self.title, lang=''
        ).exclude(pk=self.pk)
        if found:
            raise ValidationError({'__all__': ('Language Error',)})
        return super(Menu, self).full_clean(*args, **kwargs)

    def update_cache(self):
        self.menucache.cache = self._render_no_sel()
        self.menucache.save()

    def save(self, *args, **kwargs):
        if self.is_child_node():
            return super(Menu, self).save(*args, **kwargs)
        try:
            cache = self.menucache
        except MenuCache.DoesNotExist:
            cache = MenuCache.objects.create()
            self.content_object = cache
        menu = super(Menu, self).save(*args, **kwargs)
        for child in self.get_children():
            slug = getattr(child.content_object, 'slug', None)
            if slug:
                if not slug == child.slug:
                    child.slug = slug
                    child.save()
        cache.menu = self
        cache.save()
        return menu

    def children_list(self, for_admin=False):

        entry_cnt = 0

        def get_child_data(for_admin, entry, obj, dict_parent):
            if for_admin:
                reverseurl = get_adminedit_url(obj)
                return{
                    'entry_order_id': entry_cnt,
                    'entry_pk': entry.pk,
                    'entry_del_url': reverse(
                        'admin:menus_menuentry_delete',
                        args=(entry.pk, )),
                    'entry_change_url': reverse(
                        'admin:menus_menuentry_change',
                        args=(entry.pk,)),
                    'obj_admin_url': reverseurl,
                    'obj_classname': get_classname(obj.__class__),
                    'obj_title': obj,
                    'obj_status': 'published' if getattr(
                        obj, 'enabled', True) else 'draft',
                    'entry_enabled':
                        "checked" if entry.enabled else ""
                }
            if not getattr(obj, 'is_published', True):
                return {}

            child_data = {'entry_url': entry.get_absolute_url(), "dict_parent": dict_parent}
            cslug = getattr(obj, 'slug', getattr(obj, 'menukey', slugify('%s' % obj)))
            curr_dict = child_data
            while curr_dict:
                curr_dict['select_class_marker'] = curr_dict.get('select_class_marker', '')
                curr_dict['select_class_marker'] += ' %(sel_' + cslug + ')s'
                curr_dict = curr_dict['dict_parent']

            return child_data

        def _children_list(children=None, for_admin=False, dict_parent=None):
            nonlocal entry_cnt
            children_filter_kwargs = {'parent': self}
            if not for_admin:
                children_filter_kwargs['enabled'] = True

            if children is None:
                children = self.get_children().filter(**children_filter_kwargs)

            nested_children = []

            for child in children:
                obj = child.content_object
                child_data = {
                    'entry_title': child.title or getattr(obj, "title", None) or obj.name,
                    'dict_parent': dict_parent
                }

                children_filter_kwargs['parent'] = child
                child_children = []
                if not for_admin and getattr(obj, 'auto_children', False):
                    child_data['auto_entry'] = True
                    child_children = obj.get_children(parent=self)
                elif dict_parent and dict_parent.get('auto_entry', False):
                    child_children = MenuEntry.objects.none()
                else:
                    child_children = child.get_children().filter(**children_filter_kwargs)

                child_data.update(get_child_data(for_admin, child, obj, dict_parent))

                entry_cnt += 1
                if child_data and child_children:
                    child_data['children'] = _children_list(
                        children=child_children, for_admin=for_admin, dict_parent=child_data)

                if child_data:
                    nested_children.append(child_data)

            return nested_children
        return _children_list(for_admin=for_admin)

    class Meta:
        verbose_name = _('Menu')
        proxy = True


class AbstractLink(models.Model):
    title = models.CharField(_('Title'), max_length=128)
    enabled = models.BooleanField(_('enabled'), default=True)

    def __str__(self):
        return self.title

    class Meta:
        abstract = True


class Link(AbstractLink):
    url = models.CharField(_('URL'), max_length=255)

    def __str__(self):
        return self.url

    def get_absolute_url(self):
        return self.url

    class Meta:
        verbose_name = _("Link")
        verbose_name_plural = _("Links")


class ViewLink(AbstractLink):
    name = models.CharField(_('Name'), max_length=255)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        choices = tuple((
            ('%s' % key, '%s' % key)
            for key in MenusConfig.entrieable_reverse_names
        ))
        if django.VERSION < (1, 9):
            self._meta.get_field('name')._choices = choices
        else:
            self._meta.get_field('name').choices = choices

    def get_absolute_url(self):
        return reverse(self.name)

    @classmethod
    def show_in_menu_add(cls):
        return len(MenusConfig.entrieable_reverse_names) > 0

    class Meta:
        verbose_name = _("View")
        verbose_name_plural = _("View")


class AutoPopulated(AbstractLink):
    '''
    Add entries from a function.

    '''
    auto_children = True
    name = models.CharField(_('Name'), max_length=255, choices=(("a", "1"),))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        choices = tuple((
            ('%s' % k, '%s' % k)
            for k in MenusConfig.entrieable_auto_children
        ))
        if django.VERSION < (1, 9):
            self._meta.get_field('name')._choices = choices
        else:
            self._meta.get_field('name').choices = choices

    def get_children(self, parent=None):
        return MenusConfig.auto_children_funcs[self.name]()

    def get_absolute_url(self):
        return "."

    @classmethod
    def show_in_menu_add(cls):
        return len(MenusConfig.entrieable_auto_children) > 0

    class Meta:
        verbose_name = _("Autopopulated Entry")
        verbose_name_plural = _("Autopopulated Entries")
