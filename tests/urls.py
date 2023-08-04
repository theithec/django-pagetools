from django.contrib import admin
from django.urls import path
from filebrowser.sites import site

from demo.urls import urlpatterns
from pagetools.pages.views import IndexView
from pagetools.sections.views import admin_pagenodesview


urlpatterns += [
    path("", IndexView.as_view(), name="index"),
]
