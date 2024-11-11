from demo_sections.views import ArticleListView
from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from filebrowser.sites import site

from pagetools.pages.views import IndexView
from pagetools.sections.views import admin_pagenodesview

urlpatterns = [
    path("", IndexView.as_view(), name="index"),  # Optional
    path("admin/filebrowser/", site.urls),
    path("grappelli/", include("grappelli.urls")),
    path("admin/", admin.site.urls),
    path("captcha/", include("captcha.urls")),
    path("polls/", include("polls.urls", namespace="polls")),
    path("", include("pagetools.urls")),
    path("pages/", include("pagetools.pages.urls", namespace="pages")),
    path("articles/", ArticleListView.as_view(), name="articles"),
    path("node/", include("pagetools.sections.urls", namespace="sections")),
    path(
        "adminnodes/<slug:slug>/",
        admin_pagenodesview,
        name="admin_pagenodesview",
    ),
    path("search/", include("pagetools.search.urls")),
    path(
        "subscribe/",
        include("pagetools.subscriptions.urls", namespace="subscriptions"),
    ),
]
if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
        path("__debug__/", include(debug_toolbar.urls)),
    ] + urlpatterns
