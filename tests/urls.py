from django.urls import path

from demo.urls import urlpatterns  # pylint: disable=no-name-in-module, import-error
from pagetools.pages.views import IndexView


urlpatterns += [
    path("", IndexView.as_view(), name="index"),
]
