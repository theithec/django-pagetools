import re

from django.conf import settings
from django.core.paginator import Page, Paginator
from django.views.generic.list import ListView


class PaginatorMixin(ListView):
    """
    Paginator Implementation
    """

    paginate_by = getattr(settings, "PAGINATE_BY", 10)
    num_pagelinks = getattr(settings, "PAGINATION_NUM_PAGELINKS", 5)

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        page: Page = context["page_obj"]
        paginator: Paginator = page.paginator
        halfrange = self.num_pagelinks // 2
        _from = max(0, page.number - halfrange - 1)
        if page.number > paginator.num_pages - halfrange:
            _from = max(0, _from - (halfrange - (paginator.num_pages - page.number)))
        until = halfrange + page.number
        if page.number <= halfrange:
            until += halfrange - page.number + 1
        context["curr_page_range"] = paginator.page_range[_from:until]

        url_for_page = self.request.get_full_path()
        if cpy := self.request.GET.copy():
            if cpy.pop("page", None):
                url_for_page = re.sub(r"[\?|&]page=\d+", "", url_for_page)
            url_for_page += "&" if cpy else "?"
        else:
            url_for_page += "?"
        context["url_for_page"] = url_for_page
        return context
