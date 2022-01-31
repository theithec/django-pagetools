from django.conf import settings
from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from pagetools.utils import filter_expired, get_adminedit_url


class TinyMCEMixin(admin.ModelAdmin):
    """
    Add tinymce media files
    """

    class Media:

        js = [
            "%sgrappelli/tinymce/jscripts/tiny_mce/tiny_mce.js" % settings.STATIC_URL,
            "%sgrappelli/tinymce_setup/tinymce_setup.js" % settings.STATIC_URL,
        ]
        """Sphinx shows this as a hardcoded string, but it is not."""


class AdminLinkMixin:
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


class PagelikeAdmin(AdminLinkMixin, DeleteExpiredMixinAdmin, TinyMCEMixin):
    """
    Prepopulate slug from title and add tinymce-media
    """

    prepopulated_fields = {"slug": ("title",)}


def delete_expired_action(modeladmin, request, queryset):
    queryset = filter_expired(queryset)
    return admin.actions.delete_selected(modeladmin, request, queryset)
