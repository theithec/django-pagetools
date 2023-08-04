from urllib.parse import quote

from django.apps import apps
from django.core.exceptions import MultipleObjectsReturned
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from grappelli.dashboard.modules import DashboardModule

from pagetools.utils import get_classname

from .models import Menu


appconf = apps.get_app_config("menus")


class MenuModule(DashboardModule):
    """
    A module that displays a pagetools.menus.menu.

     in dashboard:
     self.children.append(MenuModule(menu_title='myMenu', column=1,))

    """

    template = "menus/admin/dashboard_menu_module.html"

    def __init__(self, *args, **kwargs):
        self.menu_title = kwargs.pop("menu_title", "MainMenu")
        kwargs["title"] = kwargs.get("title", "%s: %s" % (_("Menu Overview"), self.menu_title))
        super().__init__(*args, **kwargs)
        self.menu = None

    def add_entrychildren(self, children, collected=None):
        if collected is None:
            collected = []
        for child in children:
            child["url"] = child["obj_admin_url"] + "?menu=%s" % self.menu.pk
            collected.append(child)
            child_children = child.get("children", None)
            if child_children:
                collected = self.add_entrychildren(child_children, collected)
        return collected

    def init_with_context(self, context):
        try:
            self.menu = Menu.objects.lfilter().get(title=self.menu_title)
        except (Menu.DoesNotExist, MultipleObjectsReturned):
            self.pre_content = _("Menu not found!")

            context["menu"] = {
                "name": "Create the menu",
                "url": "".join(
                    [
                        reverse("admin:menus_menu_add"),
                        "?title=",
                        quote(self.menu_title),
                    ]
                ),
            }
            context["existing"] = []
        if self.menu:
            context["menu"] = {
                "name": self.menu,
                "url": reverse("admin:menus_menu_change", args=[self.menu.pk]),
            }
            nested_children = self.menu.children_list(for_admin=True)
            context["existing"] = self.add_entrychildren(nested_children)
            for model in appconf.entrieable_models:
                self.children.append(
                    {
                        "name": get_classname(model),
                        "url": reverse(
                            "admin:%s_%s_add"
                            % (
                                model.__module__[:-7].split(".")[-1],
                                model.__name__.lower(),
                            )
                        )
                        + "?menu=%s" % self.menu.pk,
                    }
                )
        super().init_with_context(context)
        self._initialized = True
