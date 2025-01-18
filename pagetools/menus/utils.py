from django.utils.text import slugify

from .apps import MenusConfig


def entrieable_reverse_name(name, app_name=None):
    """Make menuentry available from a view

    The view specified by its reverse name must not require paramenters
    """
    fullname = "%s:%s" % (app_name, name) if app_name else name
    MenusConfig.entrieable_reverse_names.append(fullname)
    MenusConfig.entrieable_reverse_names = sorted([name for name in MenusConfig.entrieable_reverse_names if name])
    return name


def entrieable_auto_populated(name, callback):
    """Make menuentries available from a callback

    The function `callback` with must 1. not require arguments
    and 2. returns a iteratable of `MenuEntry` like objects"""
    MenusConfig.entrieable_auto_children.append(name)
    MenusConfig.auto_children_funcs[name] = callback


def get_menukey(obj, entry=None, **kwargs):
    fullkey =   ""
    if hasattr(obj, "get_menukey"):
        fullkey = obj.get_menukey()
    if not fullkey:     
        key = getattr(obj, "menukey", getattr(obj, "slug", slugify(obj)))
        modparts =  obj.__module__.split(".")
        modname = modparts[len(modparts)-2]
        fullkey = slugify("-".join(filter(None,(modname, obj.__class__.__name__, key))))
    return fullkey