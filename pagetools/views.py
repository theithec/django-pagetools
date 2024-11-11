import re

from django.conf import settings
from django.core.paginator import Page, Paginator
from django.views.generic.list import ListView


class PaginatorMixin(ListView):
    """
    Paginator Implementation
    """

    paginate_by = getattr(settings, "PAGINATE_BY", 10)
    on_each_side = getattr(settings, "PAGINATION_ON_EACH_SIDE", 2)
    on_ends = getattr(settings, "PAGINATION_ON_ENDS", 1)

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        page: Page = context["page_obj"]
        paginator: Paginator = page.paginator
        context["curr_page_range"] = paginator.get_elided_page_range(
            page.number, on_each_side=self.on_each_side, on_ends=self.on_ends
        )
        url_for_page = self.request.get_full_path()
        if cpy := self.request.GET.copy():
            if cpy.pop("page", None):
                url_for_page = re.sub(r"[\?|&]page=\d+", "", url_for_page)
            url_for_page += "&" if cpy else "?"
        else:
            url_for_page += "?"
        context["url_for_page"] = url_for_page
        return context
