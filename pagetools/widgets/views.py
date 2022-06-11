from .models import PageType
from .utils import get_areas_for_type


class WidgetViewMixin:
    """Add `areas` context data.

    Expects a `get_pagetype_name` method, see `WidgetPagelikeMixin`
    See ::class::pagetools.widgets.models.WidgetInArea
    """

    add_pagetype_promise = True
    """If set, the widget context processor will not adding areas"""

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        ptname = self.get_pagetype_name(**kwargs)
        ptype = self.get_pagetype(ptname=ptname, **kwargs)
        kwargs["areas"] = get_areas_for_type(ptype, kwargs, request=self.request)
        kwargs["pagetype_name"] = ptname
        return kwargs

    def get_pagetype(self, ptname=None, **kwargs):
        ptype = None
        if ptname is None:
            ptname = self.get_pagetype_name(**kwargs)
        if ptname:
            try:
                ptype = PageType.objects.get(name=ptname)
            except PageType.DoesNotExist:
                pass

        return ptype


class WidgetPagelikeMixin(WidgetViewMixin):
    """A `WidgetViewMixin` that tries to find the pagetype_name by kwargs or attribute"""

    def get_pagetype_name(self, **kwargs):
        ptname = kwargs.get("pagetype_name", None)
        if ptname is None:
            ptname = getattr(self, "pagetype_name", None)
        return ptname
