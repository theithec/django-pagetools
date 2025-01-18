from django.views.generic import DetailView, TemplateView
from django.urls import path, get_resolver, reverse
from django.test import RequestFactory, override_settings

from pagetools.menus.tests import MenuDataTestCase
from pagetools.menus.views import SelectedMenuentriesMixin
from pagetools.tests.test_models import ConcretePublishableLangModel

from pagetools.menus.utils import get_menukey
class DummyDetailView(SelectedMenuentriesMixin, DetailView):
    """
    To test get_context_data with DetailView
    """

    def __init__(self, *args, **kwargs):
        self.object = ConcretePublishableLangModel.objects.first()
        super(*args, **kwargs)

    model = ConcretePublishableLangModel


class DummyNonDetailView(SelectedMenuentriesMixin, TemplateView):
    """
    To test get_context_data with Non-DetailView
    """

    template_name = "test.html"

urlpatterns = [
    # custom urlconf
    path("/detail/", DummyDetailView.as_view(), name="detail"),
    path("/nondetail/", DummyNonDetailView.as_view(), name="nondetail"),
]


@override_settings(ROOT_URLCONF=__name__)
class SelectedMenuentriesMixinTest(MenuDataTestCase):
    """
    Tests context-data in a Django Mixin like a boss

    https://gist.github.co/dnmellen/6507189
    """

    def test_detail_context_data(self):
        view = DummyDetailView()
        context = view.get_context_data()
        self.assertEqual(context["menukey"], "tests-concretepublishablelangmodel-foo1")

    def test_nondetail_context_data(self):
        response = self.client.get(reverse('nondetail'))
        self.assertEqual(response.context_data["menukey"], "nondetail")