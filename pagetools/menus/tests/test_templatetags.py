from django.test import TestCase

from pagetools.menus.models import Menu, Link
from pagetools.menus.templatetags.menus_tags import MenuRenderer
from pagetools.pages.models import Page


class TemplatetagsTests(TestCase):
    def setUp(self):
        self.menu = Menu.objects.add_root(title="m1")
        self.menu.save()
        self.page1 = Page.objects.create(title="P1", slug="p1")
        self.entry1 = self.menu.children.add_child(self.page1, enabled=True)
        self.link1 = Link.objects.create(url="/foo")
        self.entry2 = self.menu.children.add_child(self.link1, enabled=True)
        self.menu.update_cache()

    def test_entries(self):
        mr = MenuRenderer("foo", "m1").render({})
        self.assertTrue(self.link1.url in mr)
        self.assertFalse(self.page1.slug in mr)
        self.page1.status = "published"
        self.page1.save()
        self.menu.update_cache()
        renderer = MenuRenderer("foo", "m1").render({})
        self.assertTrue(self.page1.slug in renderer)

    def test_hidden_subentries(self):
        link = Link.objects.create(url="/foo3")
        self.entry2.children.add_child(link, enabled=False)

        renderer = MenuRenderer("foo", "m1").render({})
        self.assertNotIn("/foo3", renderer)
