from django import template
from django.core.exceptions import ObjectDoesNotExist

from pagetools.menus.models import Menu
from pagetools import logger


register = template.Library()


class MenuRenderer(template.Node):
    def __init__(self, menukeys, menu_title):
        self.menukeys = template.Variable(menukeys)
        self.menu_title = menu_title

    def render(self, context):
        menukeys = []
        try:
            menukeys = self.menukeys.resolve(context)
            if isinstance(menukeys, str):
                menukeys = [menukeys]

        except template.VariableDoesNotExist:
            pass
        try:
            menu = Menu.objects.lfilter().select_related().get(title=self.menu_title)
        except ObjectDoesNotExist:
            logger.warning("Unknown menu requested %s", self.menu_title)
            return ""
        return menu.render(menukeys)


@register.tag(name="menu")
def do_menu(_parser, token):
    menu_title, menukeys = token.contents.split()[1:]
    return MenuRenderer(menukeys, menu_title)
