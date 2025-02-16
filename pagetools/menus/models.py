from collections import defaultdict

from django import template
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django.utils.translation import pgettext_lazy
from mptt.fields import TreeForeignKey
from mptt.managers import TreeManager
from mptt.models import MPTTModel

from pagetools import logger
from pagetools.menus.utils import get_menukey
from pagetools.models import LangManager, LangModel
from pagetools.utils import get_adminedit_url, get_classname

from .apps import MenusConfig
from .settings import MENU_TEMPLATE


class MenuEntryManager(TreeManager, LangManager):
    def add_child(self, content_object, **kwargs):
        if not getattr(content_object, "get_absolute_url", None):
            raise ValidationError(_("MenuEntry.content_object requires get_absolute_url"))
        kwargs["title"] = kwargs.get("title", str(content_object))
        kwargs["content_type"] = ContentType.objects.get_for_model(content_object, for_concrete_model=False)
        kwargs["object_id"] = content_object.pk
        kwargs["slug"] = get_menukey(content_object)
        created = False
        entry, created = self.get_or_create(**kwargs)
        if not created:
            raise ValidationError(_("Entry %(title)s already exists"), params=kwargs)
        return entry


class MenuManager(MenuEntryManager):
    def create(self, *args, **kwargs):
        raise AttributeError(_("Use 'add_child' or 'add_root' instead of 'create'"))

    def add_root(self, title, **kwargs):
        menu, created = TreeManager.get_or_create(self, title=title, parent=None, **kwargs)
        if not created:
            raise ValidationError(_("Menu %(name)s already exists"), params={"name": title})
        return menu


class MenuEntry(MPTTModel, LangModel):
    title = models.CharField(_("Title"), max_length=128)
    slug = models.CharField(_("slug"), max_length=512, help_text=(_("Slug")), default="", blank=True)
    parent = TreeForeignKey("self", null=True, blank=True, related_name="children", on_delete=models.CASCADE)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")
    enabled = models.BooleanField(default=False)
    objects = MenuEntryManager()

    def get_absolute_url(self):
        return self.content_object.get_absolute_url()

    def clean(self):
        kwargs = {
            "title": self.title,
            "lang": self.lang,
        }
        if not self.parent:  # root
            kwargs["parent__isnull"] = True

        entries = MenuEntry.objects.filter(**kwargs).exclude(pk=self.pk)
        if self.parent:  # not root
            root = self.parent.get_root()  # pylint: disable=no-member
            for entry in entries:
                if entry.get_root() == root:
                    raise ValidationError(_("An entry with this title and language already exists in menu"))
        else:  # root
            if entries:
                raise ValidationError(_("A menu with this title and language already exists"))

    def __str__(self):
        return "%s%s" % (self.title, (" (%s)" % self.lang) if self.lang else "")


@receiver(pre_delete)
def delete_content(sender, **kwargs):
    if sender in (MenuEntry, MenuCache):
        return
    try:
        object_id = int(kwargs["instance"].pk)
    except ValueError:
        return
    content_type = ContentType.objects.get_for_model(sender)
    MenuEntry.objects.filter(content_type=content_type, object_id=object_id).delete()


class SelectedEntries(defaultdict):
    def __missing__(self, key):
        return ""


class MenuCache(models.Model):
    menu = models.OneToOneField("Menu", blank=True, null=True, on_delete=models.CASCADE)
    cache = models.TextField()

    def __str__(self):
        return "Cache: %s" % self.menu

    def get_absolute_url(self):
        return ""


class Menu(MenuEntry):
    objects = MenuManager()

    def _render_no_sel(self):
        tmpl = template.loader.get_template(MENU_TEMPLATE)
        children = self.children_list()
        return tmpl.render(
            {
                "children": children,
            }
        )

    def render(self, selected):
        sel_entries = SelectedEntries()
        for sel in selected:
            sel_entries["sel_" + sel] = "active"
        use_cache = self.enabled
        tmplstr = None
        if use_cache:
            tmplstr = MenuCache.objects.get(menu=self).cache
        else:
            tmplstr = self._render_no_sel()
        logger.info(
            " TEMPLATE %s,  SELECTED: %s, KEYS: %s",
            tmplstr,
            selected,
            ", ".join(sel_entries.keys()),
        )
        rendered = tmplstr % sel_entries
        return rendered

    def update_entries(self, orderstr):
        """orderstr = jquery.mjs.nestedSortable.js / serialize()"""
        entry_strs = orderstr.split("&")
        parent = None
        for entry_str in entry_strs:
            if not entry_str:
                break
            key, parent_id = entry_str.split("=")
            br1, br2 = list(map(key.find, ("[", "]")))
            entry_id = int(entry_str[br1 + 1 : br2])
            entry = MenuEntry.objects.get(id=entry_id)
            try:
                parent = MenuEntry.objects.get(id=int(parent_id))
            except ValueError:
                parent = entry.get_root()
            entry.move_to(parent, "last-child")
            entry = MenuEntry.objects.get(pk=entry.pk)
        MenuEntry.objects.rebuild()
        self.save()

    def full_clean(self, *args, **kwargs):
        found = Menu.objects.filter(title=self.title, lang="").exclude(pk=self.pk)
        if found:
            raise ValidationError({"__all__": _("Menu with no language exists. No others allowed")})
        return super().full_clean(*args, **kwargs)

    def update_cache(self):
        self.content_object.cache = self._render_no_sel()
        self.content_object.save()

    def save(self, *args, **kwargs):
        if self.is_child_node():
            return super().save(*args, **kwargs)
        cache = self.content_object
        if not cache:
            self.content_object = MenuCache.objects.create()
            cache = self.content_object
        menu = super().save(*args, **kwargs)
        for child in self.get_children():
            slug = getattr(child.content_object, "slug", None)
            if slug and not slug == child.slug:
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
                return {
                    "entry_order_id": entry_cnt,
                    "entry_pk": entry.pk,
                    "entry_del_url": reverse("admin:menus_menuentry_delete", args=(entry.pk,)),
                    "entry_change_url": reverse("admin:menus_menuentry_change", args=(entry.pk,)),
                    "obj_admin_url": reverseurl,
                    "obj_classname": get_classname(obj.__class__),
                    "obj_title": obj,
                    "obj_status": "published" if getattr(obj, "enabled", True) else "draft",
                    "entry_enabled": "checked" if entry.enabled else "",
                }
            if not getattr(obj, "is_published", True):
                return {}

            child_data = {
                "entry_url": entry.get_absolute_url(),
                "dict_parent": dict_parent,
            }
            ckey = entry.slug or get_menukey(obj)

            print("ckey", ckey)
            curr_dict = child_data
            while curr_dict:
                curr_dict["select_class_marker"] = curr_dict.get("select_class_marker", "")
                curr_dict["select_class_marker"] += " %(sel_" + ckey + ")s"
                curr_dict = curr_dict["dict_parent"]

            return child_data

        def _children_list(children=None, for_admin=False, dict_parent=None):
            nonlocal entry_cnt
            children_filter_kwargs = {"parent": self}
            if not for_admin:
                children_filter_kwargs["enabled"] = True

            if children is None:
                children = self.get_children().filter(**children_filter_kwargs)

            nested_children = []

            for child in children:
                obj = child.content_object
                child_data = {
                    "entry_title": child.title or getattr(obj, "title", None) or obj.name,
                    "dict_parent": dict_parent,
                }

                children_filter_kwargs["parent"] = child
                child_children = []
                if not for_admin and getattr(obj, "auto_children", False):
                    child_data["auto_entry"] = True
                    child_children = obj.get_children()
                elif dict_parent and dict_parent.get("auto_entry", False):
                    child_children = MenuEntry.objects.none()
                else:
                    child_children = child.get_children().filter(**children_filter_kwargs)

                child_data.update(get_child_data(for_admin, child, obj, dict_parent))

                entry_cnt += 1
                if child_data and child_children:
                    child_data["children"] = _children_list(
                        children=child_children,
                        for_admin=for_admin,
                        dict_parent=child_data,
                    )

                if child_data:
                    nested_children.append(child_data)

            return nested_children

        return _children_list(for_admin=for_admin)

    class Meta:
        verbose_name = _("Menu")
        proxy = True


class AbstractLink(models.Model):
    title = models.CharField(_("Title"), max_length=128)
    enabled = models.BooleanField(_("enabled"), default=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.menukey = slugify(self.title)

    def __str__(self):
        return str(self.title)

    class Meta:
        abstract = True


class Link(AbstractLink):
    url = models.CharField(_("URL"), max_length=255)

    def __str__(self):
        return str(self.url)

    def get_absolute_url(self):
        return self.url

    class Meta:
        verbose_name = _("Link")
        verbose_name_plural = _("Links")


class ViewLink(AbstractLink):
    name = models.CharField(_("Name"), max_length=255)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        choices = tuple((("%s" % key, "%s" % key) for key in MenusConfig.entrieable_reverse_names))
        self._meta.get_field("name").choices = choices

    def get_absolute_url(self):
        return reverse(self.name)

    @classmethod
    def show_in_menu_add(cls):
        return len(MenusConfig.entrieable_reverse_names) > 0

    class Meta:
        verbose_name = pgettext_lazy("menus", "View")
        verbose_name_plural = pgettext_lazy("menus", "View")


class AutoPopulated(AbstractLink):
    """
    Add entries from a function.

    """

    auto_children = True
    name = models.CharField(_("Name"), max_length=255, choices=(("a", "1"),))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        choices = tuple((("%s" % k, "%s" % k) for k in MenusConfig.entrieable_auto_children))
        self._meta.get_field("name").choices = choices

    def get_children(self):
        return MenusConfig.auto_children_funcs[self.name]()

    def get_absolute_url(self):
        return "."

    @classmethod
    def show_in_menu_add(cls):
        return len(MenusConfig.entrieable_auto_children) > 0

    class Meta:
        verbose_name = _("Autopopulated Entry")
        verbose_name_plural = _("Autopopulated Entries")
