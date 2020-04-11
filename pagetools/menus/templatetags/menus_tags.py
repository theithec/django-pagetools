'''
Created on 09.05.2013

@author: Tim Heithecker
'''
from django import template
from django.core.exceptions import ObjectDoesNotExist
from pagetools.menus.models import Menu

register = template.Library()


class MenuRenderer(template.Node):
    def __init__(self, menukeys, menu_title):
        self.menukeys = template.Variable(menukeys)
        self.menu_title = menu_title

    def render(self, context):
        menukeys = []
        try:
            menukeys = self.menukeys.resolve(context)
            if type(menukeys) not in (list, tuple):
                menukeys = [menukeys]

        except template.VariableDoesNotExist:
            pass
        try:
            menu = Menu.objects.lfilter().select_related().get(
                title=self.menu_title)
        except ObjectDoesNotExist:
            e = "<!--UNKNOWN MENU %s !-->" % self.menu_title
            return e
        return menu.render(menukeys)


@register.tag(name="menu")
def do_menu(parser, token):
    menu_title, menukeys = token.contents.split()[1:]
    return MenuRenderer(menukeys, menu_title)
