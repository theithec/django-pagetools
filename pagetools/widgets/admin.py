from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.http.response import HttpResponseRedirect
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from pagetools.models import admin_attr_decorator
from pagetools.utils import get_adminedit_url, get_classname, get_perm_str

from .models import (
    BaseWidget,
    ContentWidget,
    PageType,
    TemplateTagWidget,
    TypeArea,
    WidgetInArea,
)
from .utils import itersubclasses


class WidgetInAreaAdmin(admin.TabularInline):
    model = WidgetInArea
    fields = (
        "adminedit_url",
        "enabled",
        "position",
    )
    sortable_field_name = "position"
    extra = 0
    max_num = 0
    readonly_fields = ("adminedit_url",)

    @admin_attr_decorator
    def adminedit_url(self, instance):
        obj = instance.content_object
        return format_html('<a href="{0}">{1}</a>', get_adminedit_url(obj), f"{obj} ({obj._meta.verbose_name})" )
    adminedit_url.short_description = "Widget"


class TypeAreaAdmin(admin.ModelAdmin):
    inlines = (WidgetInAreaAdmin,)
    list_filter = ["area", "pagetype"]
    fields = ["lang", "pagetype", "area"]
    list_display = ["get_name", "widgets_overview"]

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        objs_to_add = form.data.getlist("add_objs[]")
        for txt in objs_to_add:
            pks = txt.split("_")
            contenttype = ContentType.objects.get_for_id(int(pks[0]))
            obj_id = int(pks[1])
            pos = obj.widgets.count()
            WidgetInArea.objects.get_or_create(typearea=obj, content_type=contenttype, object_id=obj_id, position=pos)

    def render_change_form(self, request, context, add=False, change=False, form_url="", obj=None):
        if obj:
            context["addable_objs"] = []
            context["addable_widgets"] = []
            found = [widget.content_object for widget in obj.widgets.all()]
            self.readonly_fields = ("area", "pagetype")
            clslist = sorted(itersubclasses(BaseWidget), key=lambda cls: cls.__name__)
            for cls in clslist:
                if not request.user.has_perm(get_perm_str(cls)):
                    continue

                context["addable_widgets"].append(
                    '<li>+  <a href="%s">%s</a></li>'
                    % (
                        (
                            reverse("admin:%s_%s_add" % (cls._meta.app_label, cls._meta.model_name))
                            + "?typearea=%s" % (context["object_id"])
                        ),
                        get_classname(cls),
                    )
                )
                instances = cls.objects.order_by("-title")
                ctpk = ContentType.objects.get_for_model(cls).pk
                for inst in instances:
                    if inst in found:
                        continue
                    context["addable_objs"].append(
                        #'<option value="%s_%s">%s</option>'
                        f'<input type="checkbox" name="add_objs[]" value="{ctpk}_{inst.pk}">{inst} ({inst._meta.verbose_name})<br>'
                    )
            self.change_form_template = "admin/widgets/typearea/change_form.html"
        else:
            self.change_form_template = "pagetools/admin/change_form_help_text.html"
            context["help_text"] = "[save] before adding widgets"
        return admin.ModelAdmin.render_change_form(
            self, request, context, add=add, change=change, form_url=form_url, obj=obj
        )

    @admin_attr_decorator
    def widgets_overview(self, instance):
        if instance:
            return ", ".join([str(wdg.content_object) for wdg in instance.widgets.all()])
        return "-"
    widgets_overview.short_description = _("Included Widgets")

    @admin_attr_decorator
    def get_name(self, instance):
        if instance:
            return str(instance)
        return "-"
    get_name.short_description = _("Pagetype-Area")

    def get_readonly_fields(self, request, obj=None):
        return ["area", "pagetype", "widgets_overview"] if obj else []


class BaseWidgetAdmin(admin.ModelAdmin):
    save_as = True
    list_display = ["name", "title", "used_by"]
    readonly_fields = [
        "used_by",
    ]

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        obj.save()
        typearea_id = request.GET.get("typearea", None)
        if typearea_id:
            typearea = TypeArea.objects.get(pk=int(typearea_id))
            WidgetInArea.objects.create(
                typearea=typearea,
                content_type=ContentType.objects.get_for_model(obj),
                object_id=obj.pk,
                position=typearea.widgets.count(),
            )

    def _redirect(self, action, request, obj, *args, **kwargs):
        typearea_id = request.GET.get("typearea", None)
        if typearea_id and "_save" in request.POST:
            return HttpResponseRedirect(reverse("admin:widgets_typearea_change", args=(typearea_id,)))

        # see menus.admin._redirect
        return getattr(admin.ModelAdmin, "response_%s" % action)(self, request, obj, *args, **kwargs)

    def response_add(self, request, obj, *args, **kwargs):
        return self._redirect("add", request, obj, *args, **kwargs)

    def response_change(self, request, obj, *args, **kwargs):
        return self._redirect("change", request, obj, *args, **kwargs)

    def used_by(self, obj):
        return mark_safe(
            ", ".join(
                [
                    f'<a href="{get_adminedit_url(wia.typearea)}">{wia.typearea}</a>'
                    for wia in obj.adapter.select_related("typearea").filter(enabled=True)
                ]
            )
        )


class PageTypeAdmin(admin.ModelAdmin):
    model = PageType


class ContentWidgetAdmin(BaseWidgetAdmin):
    pass


class TemplateTagWidgetAdmin(BaseWidgetAdmin):
    def get_readonly_fields(self, request, obj=None):
        if obj:
            self.prepopulated_fields = {}
            return ["renderclasskey"]

        self.prepopulated_fields = {"name": ("renderclasskey",)}
        return []


admin.site.register(TypeArea, TypeAreaAdmin)
admin.site.register(ContentWidget, ContentWidgetAdmin)
admin.site.register(TemplateTagWidget, TemplateTagWidgetAdmin)
admin.site.register(WidgetInArea)
admin.site.register(PageType, PageTypeAdmin)
