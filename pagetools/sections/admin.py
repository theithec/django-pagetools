from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.db.models.fields import BLANK_CHOICE_DASH
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from grappelli.forms import GrappelliSortableHiddenMixin
from pagetools.admin import AdminLinkMixin, PagelikeAdmin

from .models import PageNode, PageNodePos


class BasePageNodePosAdmin(AdminLinkMixin, GrappelliSortableHiddenMixin, admin.TabularInline):
    model = PageNodePos
    readonly_fields = ("admin_link",)
    fk_name = "owner"
    sortable_field_name = "position"
    extra = 1

    def get_queryset(self, request):
        request.parent_model = self.parent_model
        return (
            super(BasePageNodePosAdmin, self)
            .get_queryset(request)
            .select_related("owner")
            .prefetch_related("content__content_object")
        )

    def admin_link(self, instance, linktext=None):
        realobj = instance.content.content_object
        return super().admin_link(realobj, linktext)

    admin_link.short_description = _("Admin link")  # type: ignore

    def has_add_permission(self, request, obj=None):
        return True

    def formfield_for_foreignkey(self, db_field, request, **kwargs):

        is_content_with_choices = db_field.name == "content" and getattr(
            self.parent_model, "allowed_children_classes", False
        )
        if is_content_with_choices:
            cache = getattr(request, "_cache", {})
            if not cache:
                allowed_children_classes = self.parent_model.allowed_children_classes
                if len(allowed_children_classes) == 1:
                    queryset = allowed_children_classes[0].objects.all()
                else:
                    allowed_contenttypes = [
                        ContentType.objects.get_for_model(acc, for_concrete_model=False).pk
                        for acc in allowed_children_classes
                    ]
                    queryset = PageNode.objects.filter(content_type_pk__in=allowed_contenttypes)
                queryset = queryset.order_by("title")
                cache["choices"] = [("", BLANK_CHOICE_DASH)] + [(obj.id, str(obj)) for obj in queryset]
                cache["queryset"] = queryset
                request._cache = cache  # pylint: disable=protected-access
            kwargs["queryset"] = cache["queryset"]
        field = super(BasePageNodePosAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)
        if is_content_with_choices:
            field.choices = cache["choices"]
        return field


class BasePageNodeAdmin(PagelikeAdmin):

    inlines = [BasePageNodePosAdmin]
    change_form_template = "admin/change_form_chooser.html"

    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("status_changed", "containing_nodes")

    def get_queryset(self, request):
        real_pk = self.model.get_contenttype_pk()
        manager = self.model._default_manager  # pylint: disable=protected-access
        return manager.filter(content_type_pk=real_pk).prefetch_related("content_object")

    def containing_nodes(self, instance):
        parents = instance.in_nodes.all()
        txt = ", ".join([self.admin_link(p.content_object, str(p.content_object)) for p in parents])
        return mark_safe(txt)

    containing_nodes.short_description = _("Parents")  # type: ignore
    containing_nodes.allow_tags = _("Parents")  # type: ignore


admin.site.register([PageNode, PageNodePos])
