from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.views.generic import DetailView
from django_ajax.decorators import ajax
from django_ajax.mixin import AJAXMixin

from pagetools.menus.views import SelectedMenuentriesMixin
from pagetools.widgets.views import WidgetPagelikeMixin

from .dashboard_modules import PageNodesModule
from .models import PageNode
from .utils import get_template_names_for_obj


class BaseNodeView(DetailView):
    model = PageNode
    template_suffix = ""

    def get_queryset(self, *_args, **_kwargs):
        return self.model.public.lfilter(user=self.request.user)

    def get_object(self, *args, **kwargs):
        obj = super().get_object(*args, **kwargs)
        return obj.get_real_obj()

    def get_template_names(self):
        return (
            self.template_name
            or get_template_names_for_obj(self.object, self.template_suffix)
            or super().get_template_names()
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.object = self.get_object()  # pylint: disable=attribute-defined-outside-init
        context["contents"] = self.object.ordered_content(user=self.request.user)
        return context


class PagelikeNodeView(SelectedMenuentriesMixin, WidgetPagelikeMixin, BaseNodeView):
    pass


class BaseAjaxNodeViewMixin(AJAXMixin):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["AJAXVIEW"] = True
        context["css_block"] = "css_ajax"
        context["js_block"] = "js_ajax"
        return context


class BaseAjaxNodeView(BaseAjaxNodeViewMixin, BaseNodeView):
    template_suffix = "_ajax"


def _add_children(txt, children, user):
    for child in children:
        adminediturl = reverse(
            "admin:%s_%s_change" % (child._meta.app_label, child._meta.model_name),
            args=(child.id,),
        )

        txt += format_html(
            """<li><a {} href="{}">{}</a>""",
            "" if child.is_published else mark_safe("style='color: orange;'"),
            adminediturl,
            child,
        )
        coc = child.ordered_content(user=user)
        if coc:
            txt += "<ul>" + _add_children("", coc, user) + "</ul>"
        txt += "</li>"
    return txt


@ajax
@login_required
def admin_pagenodesview(request, slug):
    module = PageNodesModule.model.objects.get(slug=slug)
    listtxt = '<ol id="pagenodes">'
    listtxt += _add_children("", [module], user=request.user)
    listtxt += "</ol>"
    return HttpResponse(listtxt)
