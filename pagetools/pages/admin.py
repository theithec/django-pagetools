from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from pagetools.admin import PagelikeAdmin
from pagetools.menus.admin import EntrieableAdmin
from pagetools.menus.models import MenuEntry
from pagetools.menus.utils import entrieable_auto_populated
from pagetools.pages.models import Page  # , DynFormField, PageDynFormField


class BasePageAdmin(EntrieableAdmin, PagelikeAdmin):
    readonly_fields = ("status_changed",)
    list_display = ("title", "lang", "slug", "status")
    list_filter = ("lang", "status")
    search_fields = ("title", "content")
    save_as = True


class PageAdmin(BasePageAdmin):
    fieldsets = (
        (
            "",
            {
                "fields": [
                    "lang",
                    "status",
                    "title",
                    "slug",
                    "description",
                    "content",
                ]
            },
        ),
        (
            _("Included form"),
            {
                "fields": [
                    "included_form",
                    "email_receivers",
                ]
            },
        ),
        (
            _("Protection"),
            {
                "fields": [
                    "login_required",
                ]
            },
        ),
        (
            _("Show in menus"),
            {
                "fields": [
                    "menus",
                ]
            },
        ),
        (
            _("Pagetype"),
            {
                "fields": [
                    "pagetype",
                ]
            },
        ),
    )

    class Meta:
        model = Page


admin.site.register(Page, PageAdmin)


def pages_auto_entries():
    return [MenuEntry(title=p.title, content_object=p) for p in Page.public.all()]


entrieable_auto_populated("All pages", pages_auto_entries)
