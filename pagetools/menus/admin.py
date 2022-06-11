from django import forms
from django.conf import settings
from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.http.response import HttpResponseRedirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from pagetools.admin import TinyMCEMixin
from pagetools.utils import get_adminadd_url, get_classname

from .apps import MenusConfig
from .models import AutoPopulated, Link, Menu, MenuCache, MenuEntry, ViewLink


class MenuChildrenWidget(forms.Widget):
    """
    Drag and dropable menu entries
    """

    def __init__(self, *args, **kwargs):
        self.instance = kwargs.pop("instance", None)
        super().__init__(*args, **kwargs)

    def render(self, *_args, **_kwargs):
        menu = Menu.objects.get(pk=self.instance.pk)
        return mark_safe(
            render_to_string(
                "menus/admin/menuentries.html",
                {
                    "children": menu.children_list(for_admin=True),
                    "cls": 'class="sortable grp-grp-items sortable ui-sortable '
                    'mjs-nestedSortable-branch mjs-nestedSortable-expanded"',
                    "original": menu,
                },
            )
        )


class MenuAddForm(forms.ModelForm):
    class Meta:
        model = Menu
        fields = ("lang", "title")


class MenuChangeForm(forms.ModelForm):
    children = forms.Field()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["children"] = forms.Field(required=False, widget=MenuChildrenWidget(instance=kwargs["instance"]))
        self.fields["enabled"].short_description = "FOO"

    def clean_children(self, *args, **_kwargs):
        names = []
        cnt = 0
        while True:
            try:
                name = self.data["entry-text-%s" % cnt]
            except KeyError:
                break
            if name in names:
                raise ValidationError(_('Entry "%s" already exists' % name))
            names.append(name)
            cnt += 1

    class Meta:
        model = Menu
        fields = ("lang", "title", "children", "enabled")
        labels = {
            "enabled": "Use Cache",
        }


class MenuAdmin(TinyMCEMixin, admin.ModelAdmin):
    save_as = True
    list_display = ("title", "lang")

    def get_form(self, request, obj=None, **kwargs):  # pylint: disable=arguments-differ
        # Proper kwargs are form, fields, exclude, formfield_callback
        if obj:
            self.readonly_fields = ("addable_entries",)
            self.form = MenuChangeForm
        else:
            self.readonly_fields = ()
            self.form = MenuAddForm
        return super().get_form(request, obj, **kwargs)

    def addable_entries(self, obj, **_kwargs):
        ems = MenusConfig.entrieable_models
        txt = "<ul>"
        for mod in ems:
            txt += '<li><a href="%s?menus=%s">%s</a></li>' % (
                get_adminadd_url(mod),
                obj.pk,
                get_classname(mod),
            )
        return mark_safe(txt + "</ul>")

    addable_entries.short_description = _("Add")  # type: ignore
    addable_entries.allow_tags = True  # type: ignore

    def get_queryset(self, request):
        return Menu.objects.root_nodes()

    def render_change_form(self, request, context, add=False, change=False, form_url="", obj=None):
        if change and obj:
            context["addable_entries"] = mark_safe(
                "".join(
                    [
                        '<li><a href="%s?menu=%s">%s</a></li>'
                        % (
                            get_adminadd_url(model),
                            context["object_id"],
                            get_classname(model),
                        )
                        for model in MenusConfig.entrieable_models
                    ]
                )
            )
            menu_obj = Menu.objects.filter(pk=obj.pk)[0]
            context["menu_entries"] = menu_obj.children_list(for_admin=True)
        return admin.ModelAdmin.render_change_form(
            self, request, context, add=add, change=change, form_url=form_url, obj=obj
        )

    def save_related(self, request, form, formsets, change):
        obj = Menu.objects.get(pk=form.instance.pk)
        entry_order = form.data.get("entry-order")
        if entry_order:
            obj.update_entries(entry_order)

        cnt = 0
        while True:
            try:
                eid = form.data["entry-order-id-%s" % cnt]
                name = form.data["entry-text-%s" % cnt]
                ispub = form.data.get("entry-published-%s" % cnt, 0)
            except KeyError:
                break
            entry = MenuEntry.objects.get(pk=eid)
            entry.title = name
            entry.enabled = ispub == "1"
            entry.save()
            cnt += 1
        if obj.enabled:
            obj.update_cache()

    class Meta:
        model = Menu

    class Media:
        js = (
            "pagetools/admin/js/jquery.min.js",
            "pagetools/admin/js/jquery-ui.min.js",
            "pagetools/admin/js/jquery.mjs.nestedSortable.js",
            "pagetools/admin/js/menuentries.js",
        )
        css = {"all": ("pagetools/admin/css/menuentries.css",)}


class EntrieableForm(forms.ModelForm):
    """Adds a field: menus to the form. Preselect all menus which contain an
    entry for the obj
    """

    menus = forms.Field()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.existing_menuentries = []
        self.sel_menus = None
        menus = [(m.id, "%s" % m) for m in Menu.objects.root_nodes()]
        try:
            entry = kwargs["instance"]
            content_type = ContentType.objects.get_for_model(entry)
            containing_menus = MenuEntry.objects.filter(content_type=content_type, object_id=entry.id)
            menuroot_ids = {menu.get_root().id for menu in containing_menus}
        except (KeyError, AttributeError):
            menuroot_ids = set()

        self.fields["menus"] = forms.MultipleChoiceField(
            label=_("Menus"),
            choices=menus,
            required=False,
            initial=list(menuroot_ids),
            widget=forms.CheckboxSelectMultiple,
        )

    def clean(self):
        cleaned_data = super().clean()
        if self.instance and "menus" in self.changed_data:
            obj = self.instance
            cmp_data = self.cleaned_data.copy()
            fmenu_ids = [int(m) for m in cmp_data.pop("menus", [])]
            self.sel_menus = Menu.objects.filter(id__in=fmenu_ids)
            existing_menuentries_for_obj = MenuEntry.objects.filter(
                content_type=ContentType.objects.get_for_model(obj.__class__),
                object_id=obj.pk,
            )
            for entry in existing_menuentries_for_obj:
                entry.clean()
                self.existing_menuentries.append(entry)
        return cleaned_data

    class Media(TinyMCEMixin.Media):
        js = TinyMCEMixin.Media.js + [settings.STATIC_URL + "pagetools/admin/js/pre_sel_menu.js"]


class EntrieableAdmin(admin.ModelAdmin):

    form = EntrieableForm
    is_menu_entrieable = True

    def get_fields(self, request, obj=None):
        """
        See :func:`pagetools.menus.admin.entrieable_admin_get_fields`
        """
        superfunc = super(self.__class__, self).get_fields
        if not getattr(superfunc, "for_entrieable", False):
            fields = superfunc(request, obj)
        else:
            fields = admin.ModelAdmin.get_fields(self, request, obj)

        if "menus" not in fields:
            fields = fields + type(fields)(("menus",))
        return fields

    get_fields.for_entrieable = True  # type: ignore

    def get_fieldsets(self, request, obj=None):
        superfunc = super(self.__class__, self).get_fieldsets
        if not getattr(superfunc, "for_entrieable", False):
            self.fieldsets = superfunc(request, obj)
        else:
            self.fieldsets = super().get_fieldsets(request, obj)

        added = False
        for fieldset in self.fieldsets:
            if "menus" in fieldset[1]["fields"]:
                added = True
                break

        if not added:
            self.fieldsets = self.fieldsets + type(self.fieldsets)(((_("In menus"), {"fields": ["menus"]}),))

        return self.fieldsets

    get_fieldsets.for_entrieable = True  # type: ignore

    def save_related(self, request, form, formsets, change):
        """Entrieable save_related (for monkeypatching)"""
        superfunc = super(self.__class__, self).save_related
        if not getattr(superfunc, "for_entrieable", False):
            superfunc(request, form, formsets, change)
        else:
            admin.ModelAdmin.save_related(self, request, form, formsets, change)

        if "menus" not in form.changed_data:
            return

        existing_menuentries = form.existing_menuentries
        all_menus = Menu.objects.root_nodes()
        for menu in all_menus:
            found = None
            for entry in existing_menuentries:
                if entry.parent.get_root().pk == menu.pk:
                    found = entry
                    break

            is_selected = menu in form.sel_menus
            if is_selected and not found:
                root = Menu.objects.get(pk=menu.pk)
                title = getattr(form.instance, "title", None)
                kwargs = {}
                if title:
                    kwargs["title"] = title

                entry = root.children.add_child(form.instance, **kwargs)
                entry.move_to(root, "last-child")
                entry.save()

            elif found and not is_selected:
                entry.delete()  # pylint: disable=undefined-loop-variable

    save_related.for_entrieable = True  # type: ignore

    def _redirect(self, action, request, obj, *args, **kwargs):
        menus_param = request.GET.get("menus", None)
        if menus_param and "_save" in request.POST:
            return HttpResponseRedirect(reverse("admin:menus_menu_change", args=(menus_param,)))

        return getattr(admin.ModelAdmin, "response_%s" % action)(self, request, obj, *args, **kwargs)

    def response_add(self, request, obj, *args, **kwargs):
        return self._redirect("add", request, obj, *args, **kwargs)

    def response_change(self, request, obj, *args, **kwargs):
        return self._redirect("change", request, obj, *args, **kwargs)


def make_entrieable_admin(clz):
    """
    Monkeypatch an admin class

    Call this with an admin class to allow the instance class to
    be a menu entry.
    """

    clz.is_menu_entrieable = True
    clz.save_related = EntrieableAdmin.save_related
    clz.get_fields = EntrieableAdmin.get_fields
    clz.get_fieldsets = EntrieableAdmin.get_fieldsets
    clz.form = EntrieableForm


class MenuEntryAdmin(admin.ModelAdmin):
    list_display = ("title", "lang", "enabled")
    list_filter = ("lang", "enabled")


admin.site.register(Menu, MenuAdmin)
admin.site.register(Link, EntrieableAdmin)
admin.site.register(ViewLink, EntrieableAdmin)
admin.site.register(MenuEntry, MenuEntryAdmin)
admin.site.register(MenuCache)
admin.site.register(AutoPopulated, EntrieableAdmin)
