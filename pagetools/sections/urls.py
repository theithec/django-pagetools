from django.urls import path

from pagetools.sections.views import BaseAjaxNodeView, PagelikeNodeView

app_name = "sections"

urlpatterns = [
    path("ajaxnode/<slug:slug>/", BaseAjaxNodeView.as_view(), name="ajax"),
    path("<slug:slug>/", PagelikeNodeView.as_view(), name="node"),
]
