from django.test import TransactionTestCase

from pagetools.menus.models import Link, Menu
from pagetools.pages.models import Page
from pagetools.settings import STATUS_PUBLISHED
from pagetools.tests.test_models import ConcretePublishableLangModel


class MenuDataTestCase(TransactionTestCase):
    # fixtures = ["testdata.json"]
    def setUp(self):
        super().setUp()
        kwargs = {"enabled": True}
        self.menu = Menu.objects.add_root(title="MainMenu")
        self.page1 = Page.objects.create(
            title="P1",
            slug="start",
            status=STATUS_PUBLISHED,
            included_form="Contactform",
        )
        self.entry_page1 = self.menu.children.add_child(self.page1, **kwargs)
        self.link1 = Link.objects.create(url="#")
        self.entry_link1 = self.menu.children.add_child(self.link1, **kwargs)
        self.cpm1 = ConcretePublishableLangModel.objects.create(foo="foo1", status=STATUS_PUBLISHED)
        self.entry_cpm1 = self.menu.children.add_child(self.cpm1, **kwargs)
