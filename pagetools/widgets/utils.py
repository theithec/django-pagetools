from django.db.utils import DatabaseError

from pagetools.widgets.models import PageType, TypeArea


def type_or_none(typename):
    try:
        return PageType.objects.get(name=typename)
    except (PageType.DoesNotExist, DatabaseError):
        return None


def get_areas_for_type(pagetype, contextdict, request, tmpdict=None):
    request.areas_added = True
    if not tmpdict:
        tmpdict = {}

    if pagetype is None:
        pagetype = type_or_none("base")
        if not pagetype:
            return None

        return get_areas_for_type(pagetype, contextdict, request, tmpdict)
    type_areas = TypeArea.objects.lfilter(pagetype=pagetype)
    for type_area in type_areas:
        if tmpdict.get(type_area.area) is not None:
            continue

        orderedwidgets = type_area.widgets.filter(enabled=True).prefetch_related("content_object").order_by("position")
        tmpdict[type_area.area] = [widget.get_content(contextdict, request) for widget in orderedwidgets]

    if pagetype.parent:
        tmpdict = get_areas_for_type(pagetype.parent, contextdict, request, tmpdict)
    return tmpdict


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
