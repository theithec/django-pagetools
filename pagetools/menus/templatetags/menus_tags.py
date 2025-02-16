from django import template
from django.core.exceptions import ObjectDoesNotExist

from pagetools.menus.models import Menu
from pagetools import logger


register = template.Library()


class MenuRenderer(template.Node):
    def __init__(self, menukey, menu_title):
        self.menukey = template.Variable(menukey)
        self.menu_title = menu_title

    def render(self, context):
        menukey = []
        try:
            menukey = self.menukey.resolve(context)
            if isinstance(menukey, str):
                menukey = [menukey]

        except template.VariableDoesNotExist:
            pass
        try:
            menu = Menu.objects.lfilter().select_related().get(title=self.menu_title)
        except ObjectDoesNotExist:
            logger.warning("Unknown menu requested %s", self.menu_title)
            return ""
        return menu.render(menukey)


@register.tag(name="menu")
def do_menu(_parser, token):
    menu_title, menukey = token.contents.split()[1:]
    return MenuRenderer(menukey, menu_title)
