from pagetools.views import PaginatorMixin

from .models import Article


class ArticleListView(PaginatorMixin):
    paginate_by = 5
    model = Article
