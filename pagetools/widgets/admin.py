from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.http.response import HttpResponseRedirect
from django.urls import reverse

from pagetools.admin import TinyMCEMixin
from pagetools.utils import get_classname, get_perm_str

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


class TypeAreaAdmin(admin.ModelAdmin):
    inlines = (WidgetInAreaAdmin,)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        objs_to_add = form.data.get("add_objs")
        if objs_to_add:
            pks = objs_to_add.split("_")
            contenttype = ContentType.objects.get_for_id(int(pks[0]))
            obj_id = int(pks[1])
            pos = obj.widgets.all().count()
            WidgetInArea.objects.get_or_create(typearea=obj, content_type=contenttype, object_id=obj_id, position=pos)

    def render_change_form(self, request, context, add=False, change=False, form_url="", obj=None):

        if obj:
            user = request.user
            clslist = itersubclasses(BaseWidget)
            context["addable_objs"] = []
            context["addable_widgets"] = []
            found = [widget.content_object for widget in obj.widgets.all()]
            self.readonly_fields = ("area", "pagetype")
            for cls in clslist:
                if not user.has_perm(get_perm_str(cls)):
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
                instances = cls.objects.all()
                ctpk = ContentType.objects.get_for_model(cls).pk
                for inst in instances:
                    if inst in found:
                        continue

                    context["addable_objs"].append(
                        '<option value="%s_%s">%s</option>'
                        % (
                            ctpk,
                            inst.pk,
                            inst,
                        )
                    )
            self.change_form_template = "admin/widgets/typearea/change_form.html"
        else:
            self.change_form_template = "pagetools/admin/change_form_help_text.html"
            context["help_text"] = "[save] before adding widgets"
        return admin.ModelAdmin.render_change_form(
            self, request, context, add=add, change=change, form_url=form_url, obj=obj
        )

    def get_readonly_fields(self, request, obj=None):
        return ["area", "pagetype"] if obj else []


class BaseWidgetAdmin(admin.ModelAdmin):

    save_as = True

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


class PageTypeAdmin(admin.ModelAdmin):
    model = PageType


class ContentWidgetAdmin(BaseWidgetAdmin, TinyMCEMixin):
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
