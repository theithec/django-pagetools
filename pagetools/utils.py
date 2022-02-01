# pylint: disable=protected-access, consider-using-f-string
# because a) better in utils b) not now
import importlib
from datetime import datetime, timedelta

from django.db.models import Model
from django.urls import reverse


# http://code.activestate.com/recipes/576949-find-all-subclasses-of-a-given-class/
def itersubclasses(cls, _seen=None):
    """
    itersubclasses(cls)

    Generator over all subclasses of a given class, in depth first order.

    >>> list(itersubclasses(int)) == [bool]
    True
    >>> class A(object): pass
    >>> class B(A): pass
    >>> class C(A): pass
    >>> class D(B,C): pass
    >>> class E(D): pass
    >>>
    >>> for cls in itersubclasses(A):
    ...     print(cls.__name__)
    B
    D
    E
    C
    >>> # get ALL (new-style) classes currently defined
    >>> [cls.__name__ for cls in itersubclasses(object)] #doctest: +ELLIPSIS
    ['type', ...'tuple', ...]
    """

    if not isinstance(cls, type):
        raise TypeError("itersubclasses must be called with new-style classes, not %.100r" % cls)
    if _seen is None:
        _seen = set()
    try:
        subs = cls.__subclasses__()
    except TypeError:  # fails only when cls is type
        subs = cls.__subclasses__(cls)
    for sub in subs:
        if sub not in _seen:
            _seen.add(sub)
            yield sub
            for sub in itersubclasses(sub, _seen):
                yield sub


def get_classname(cls):
    try:
        name = cls._meta.verbose_name
    except AttributeError:
        name = cls.__name__
    return name


def get_adminadd_url(cls):
    adminurl = reverse("admin:%s_%s_add" % (cls._meta.app_label, cls._meta.model_name))
    return adminurl


def get_adminedit_url(model: Model) -> str:
    return reverse(
        "admin:%s_%s_change" % (model.__class__._meta.app_label, model.__class__.__name__.lower()),
        args=(model.pk,),
    )


def get_perm_str(cls, perm="add"):
    """
    Example:

        .. code-block:: python

            if not user.has_perm(get_addperm_str(clz)):
                continue
    """
    return "%s.%s_%s" % (cls._meta.app_label, perm, cls.__name__.lower())


def importer(str_or_obj):
    """
    If the argument is a string import it with importlib
    """
    if isinstance(str_or_obj, str):
        modname, clsname = str_or_obj.rsplit(".", 1)
        str_or_obj = getattr(importlib.import_module(modname), clsname)
    return str_or_obj


def filter_expired(queryset):
    """The model needs
    define_expired = Name of a DateTimeField
    # optional
    expired_daterange = 1  # Days - how old items have to be to be deleted
    """
    model = queryset.model
    fieldname = model.define_expired
    daterange = getattr(model, "expired_daterange", 1)
    to_delete = model.objects.filter(**{"%s__lt" % fieldname: datetime.now() - timedelta(daterange)})
    return to_delete
