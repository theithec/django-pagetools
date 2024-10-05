from typing import Sequence
from django.db import models
from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import admin_attr_decorator
from .utils import filter_expired, get_adminedit_url


class AdminLinkMixin:
    @admin_attr_decorator
    def admin_link(self, instance, linktext=None):
        linktext = linktext or "Edit"
        return format_html('<a href="{}">{}</a>', get_adminedit_url(instance), linktext)

    admin_link.short_description = _("Admin link")


class DeleteExpiredMixinAdmin:
    def get_actions(self, request):
        actions = super().get_actions(request)
        if getattr(self.model, "define_expired", None):
            actions["delete_expired"] = (
                delete_expired_action,
                "delete_expired",
                _("Delete expired"),
            )
        return actions


class PagelikeAdmin(AdminLinkMixin, DeleteExpiredMixinAdmin):
    """
    Prepopulate slug from title
    """
    model: models.Model
    prepopulated_fields: dict[str, Sequence[str]] = {"slug": ["title",]}


def delete_expired_action(modeladmin, request, queryset):
    queryset = filter_expired(queryset)
    return admin.actions.delete_selected(modeladmin, request, queryset)
