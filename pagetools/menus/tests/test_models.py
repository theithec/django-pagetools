from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils.translation import get_language
from django.utils.translation import gettext_lazy as _

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
        self.assertEqual(self.entry_page1.slug, "pages-page-start")

    def test_renamed_entry_slugs(self):
        self.page1.slug = "P1"
        self.page1.save()
        self.menu.save()
        self.assertEqual(self.menu.get_children()[0].slug, "P1")

    def test_doubleslug(self):
        with self.assertRaises(ValidationError):
            self.menu.children.add_child(self.page1)

    def test_created(self):
        self.assertEqual(self.page1, self.menu.children.first().content_object)

    def test_frobidden_create(self):
        with self.assertRaises(AttributeError) as err:
            Menu.objects.create(name="M2")
            self.assertEqual(str(err), _("Use 'add_child' or 'add_root' instead of 'create'"))

    def test_invalid_creation(self):
        with self.assertRaises(ValidationError) as err:
            self.menu.children.add_child("Just as string")
            self.assertEqual(str(err), "MenuEntry.content_object requires get_absolute_url")

    def test_menu_already_exists(self):
        with self.assertRaises(ValidationError) as err:
            Menu.objects.add_root("MainMenu")
            self.assertEqual(str(err), "Menu M1 already exists")

    def test_entry(self):
        with self.assertRaises(ValidationError) as ctx:
            Menu.objects.add_child(self.page1)
        self.assertEqual(str(ctx.exception), "['Entry P1 already exists']")
