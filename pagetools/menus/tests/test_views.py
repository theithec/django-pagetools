from django.views.generic import DetailView, TemplateView

from pagetools.menus.tests import MenuDataTestCase
from pagetools.menus.views import SelectedMenuentriesMixin
from pagetools.tests.test_models import ConcretePublishableLangModel


class DummyDetailView(SelectedMenuentriesMixin, DetailView):
    """
    To test get_context_data with DetailView
    """

    def __init__(self, *args, **kwargs):
        self.object = ConcretePublishableLangModel.objects.first()
        super(*args, **kwargs)
        # self.menukey = f"concretepublishablelangmodel-{self.object.foo}"

    model = ConcretePublishableLangModel


class DummyNonDetailView(SelectedMenuentriesMixin, TemplateView):
    """
    To test get_context_data with Non-DetailView
    """

    template_name = "any_template.html"
    menukey = "" #tests-dummynondetailview"

    #def __str__(self):
    #    return "tests-dummynondetailview"


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
        view = DummyNonDetailView()
        context = view.get_context_data()
        print("CC", context["menukey"])
        self.assertEqual(context["menukey"], "tests-dummynondetailview")