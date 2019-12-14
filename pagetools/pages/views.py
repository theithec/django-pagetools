# Create your views here.
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.http.response import Http404
from django.http import JsonResponse
from django.utils.translation import ugettext as _
from django.views.generic.detail import DetailView

from pagetools.widgets.views import WidgetPagelikeMixin
from pagetools.menus.views import SelectedMenuentriesMixin
from .models import Page


class IncludedFormMixin:
    '''
        expects in object
        includable_forms = { 'name1': Form1,
         [...]
        }

    '''
    included_form = None
    success_url = "/"

    def get_form_class(self):
        self.object = self.get_object()
        fname = self.object.included_form
        if fname:
            return self.object.includable_forms.get(fname)
        return None

    def get(self, request, *_args, **kwargs):
        form_class = self.get_form_class()
        if form_class and kwargs.get('form', None) is None:
            formcls = self.get_form_class()
            fkwargs = self.get_form_kwargs()
            kwargs['form'] = formcls(**fkwargs)
        return self.render_to_response(self.get_context_data(**kwargs))

    def post(self, request, *_args, **kwargs):
        self.get_object()
        form = self.get_form_class()(request.POST, **self.get_form_kwargs())
        if form.is_valid():
            kwargs['form'] = None
            return self.form_valid(form)

        return self.form_invalid(form)

    def form_valid(self, form):
        if self.request.is_ajax():
            return JsonResponse({'data': _("Mail send")}, status=200)

        messages.success(self.request, _("Mail send"))
        return self.get(self.request, form=None)

    def form_invalid(self, form):
        if self.request.is_ajax():
            return JsonResponse(form.errors, status=400)
        messages.error(self.request, _("An error occured"))
        return self.get(self.request, form=form)

    def get_form_kwargs(self):
        kwargs = {}
        if getattr(self, 'object') and getattr(self.object, 'email_receivers_list'):
            kwargs['mailreceivers'] = self.object.email_receivers_list()
        return kwargs


class AuthPageMixin:

    def get_queryset(self, *_args, **kwargs):

        user = self.request.user
        if not user.is_authenticated:
            kwargs['login_required'] = False
        kwargs['user'] = user
        qs = self.model.public.lfilter(**kwargs)
        return qs


class BasePageView(SelectedMenuentriesMixin, WidgetPagelikeMixin, DetailView):
    pass


class PageView(
        AuthPageMixin,
        IncludedFormMixin,
        BasePageView):
    model = Page

    def get_pagetype_name(self, **kwargs):
        return (
            self.object.pagetype.name
            if self.object.pagetype
            else super().get_pagetype_name(**kwargs))

    def get_pagetype(self, **kwargs):
        return self.object.pagetype or super().get_pagetype(self)

    def get_context_data(self, **kwargs):
        kwargs['page_title'] = self.object.title
        kwargs = super(PageView, self).get_context_data(**kwargs)
        return kwargs


class IndexView(PageView):

    def get_object(self, **_kwargs):
        try:
            self.object = self.get_queryset().get(
                slug="start"
            )
            return self.object
        except ObjectDoesNotExist:
            raise Http404
