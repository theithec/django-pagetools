from django.conf.urls import include, url
from django.contrib import admin
from filebrowser.sites import site

from demo.urls import urlpatterns
from pagetools.pages.views import IndexView
from pagetools.sections.views import admin_pagenodesview


urlpatterns += [
    url(r"^$", IndexView.as_view(), name="index"),
]
