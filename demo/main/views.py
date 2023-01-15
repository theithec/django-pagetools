from demo_sections.models import Article

from pagetools.views import PaginatorMixin


class ArticleListView(PaginatorMixin):
    paginate_by = 5
    model = Article
