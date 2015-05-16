from django.shortcuts import render
from pagetools.sections.views import BaseAjaxNodeView, BaseNodeView
from .models import Page, PageNode

class NodeView(BaseNodeView):
    model = PageNode


class IndexView(NodeView):
    template_name = "base.html"


    def get_object(self, *args, **kwargs):
        self.object = Page.objects.filter(content_type_pk = Page.get_contenttype_pk()).first()
        return self.object


class AjaxNodeView(BaseAjaxNodeView):
    model = PageNode