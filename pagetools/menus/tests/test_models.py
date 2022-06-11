from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils.translation import get_language

from pagetools.menus.models import Menu
from pagetools.menus.tests import MenuDataTestCase
from pagetools.pages.models import Page


class ModelTests(MenuDataTestCase):
    def test_validation(self):
        self.assertRaises(ValidationError, self.menu.children.add_child, self.page1)

    def test_rm_and_add_again(self):
        self.entry_page1.delete()
        self.menu.save()
        self.entry_page1 = self.menu.children.add_child(self.page1)

    def test_childen(self):
        lang = get_language()
        children = self.menu.get_children()
        self.assertEqual(self.menu.title, "MainMenu")
        url1 = children[1].get_absolute_url()
        if url1.startswith("/%s/" % lang):
            url1 = url1[3:]

        url0 = children[0].get_absolute_url()
        if url0.startswith("/%s/" % lang):
            url0 = url0[3:]
        self.assertEqual(url0, self.page1.get_absolute_url())

    def test_entry_slugs(self):
        self.assertEqual(self.entry_page1.slug, "page.start")

    def test_renamed_entry_slugs(self):
        self.page1.slug = "P1"
        self.page1.save()
        self.menu.save()
        self.assertEqual(self.menu.get_children()[0].slug, "P1")

    def test_doubleslug(self):
        with self.assertRaises(ValidationError):
            self.menu.children.add_child(self.page1)


class M2Tests(TestCase):
    def test_create(self):
        menu = Menu.objects.add_root("M1")
        page = Page.objects.create(title="t1", slug="t1", content="t1", status="published")
        menu.children.add_child(page)
        self.assertEqual(page, menu.children.first().content_object)
