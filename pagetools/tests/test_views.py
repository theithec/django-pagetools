from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase, override_settings
from django.urls import path

from pagetools.tests.test_models import ConcretePublishableLangModel
from pagetools.views import PaginatorMixin


class CPLMListView(PaginatorMixin):
    model = ConcretePublishableLangModel
    template_name = "base.html"
    paginate_by = 3


urlpatterns = [
    # custom urlconf
    path("/", CPLMListView.as_view(), name="view1")
]


@override_settings(ROOT_URLCONF=__name__)
class PaginatorTest(TestCase):
    def setUp(self):
        usermodel = get_user_model()
        self.admin = usermodel.objects.create_superuser("admin", "q@w.de", "password")
        self.client.login(username="admin", password="password")
        self.factory = RequestFactory()

        for i in range(0, 4):
            ConcretePublishableLangModel.objects.create(foo="f%s" + str(i))

    def test_view(self):
        request = self.factory.get("/")
        view = CPLMListView.as_view()(request)
        self.assertEqual(list(view.context_data["curr_page_range"]), list(range(1, 3)))
