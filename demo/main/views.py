from demo_sections.models import Article

from pagetools.views import PaginatorMixin


class ArticleListView(PaginatorMixin):
    model = Article
