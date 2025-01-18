from pagetools.views import PaginatorMixin
from pagetools.menus.views import SelectedMenuentriesMixin

from .models import Article


class ArticleListView(SelectedMenuentriesMixin, PaginatorMixin):
    paginate_by = 5
    model = Article
