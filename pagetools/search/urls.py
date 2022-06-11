from django.urls import path

from pagetools.menus.utils import entrieable_reverse_name
from pagetools.search.views import SearchResultsView

urlpatterns = [path("", SearchResultsView.as_view(), name=entrieable_reverse_name("search"))]
