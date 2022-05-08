from django.conf import settings
from django.views.generic.list import ListView


class PaginatorMixin(ListView):
    """
    Paginator Implementation
    """

    paginate_by = getattr(settings, "PAGINATE_BY", 20)

    def get_context_data(self, **kwargs):
        context = super(PaginatorMixin, self).get_context_data(**kwargs)
        page = context["page_obj"]
        paginator = page.paginator
        _from = page.number - 5 if page.number > 5 else 0
        context["curr_page_range"] = paginator.page_range[_from : page.number + 5]
        url_for_page = self.request.get_full_path()
        url_for_page += "&" if self.request.GET else "?"
        context["url_for_page"] = url_for_page
        return context
