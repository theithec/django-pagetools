'''
Created on 20.12.2013

@author: lotek
'''

from django.conf import settings
from django.template.defaultfilters import slugify
from django.views.generic import View
from django.views.generic.list import ListView


class PaginatorMixin(ListView):
    '''Paginator Implemtation
    If your urls use already GET-vars set sep to ="&" in subclass'''
    paginate_by = getattr(settings, 'PAGINATE_BY', 20)
    sep = '?'

    def get_context_data(self, **kwargs):
        context = super(PaginatorMixin, self).get_context_data(**kwargs)
        page = context['page_obj']
        paginator = page.paginator
        _from = page.number - 5 if page.number > 5 else 0
        context['curr_page_range'] = paginator.page_range[_from:page.number + 5]
        context['get_sep'] = self.sep
        return context
