import re

from django.conf import settings
from django.views.generic.list import ListView


class PaginatorMixin(ListView):
    """
    Paginator Implementation
    """

    paginate_by = getattr(settings, "PAGINATE_BY", 20)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page = context["page_obj"]
        paginator = page.paginator
        _from = page.number - 5 if page.number > 5 else 0
        context["curr_page_range"] = paginator.page_range[_from : page.number + 5]
        url_for_page = self.request.get_full_path()

        if cpy := self.request.GET.copy():
            if cpy.pop("page", None):
                url_for_page = re.sub(r"[\?|&]page=\d+", "", url_for_page)
            url_for_page += "&" if cpy else "?"
        else:
            url_for_page += "?"
        context["url_for_page"] = url_for_page
        return context
