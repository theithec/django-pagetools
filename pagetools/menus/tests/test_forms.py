from django.test.testcases import TestCase
from django.urls import reverse

from pagetools.menus.admin import MenuAddForm, MenuChangeForm
from pagetools.menus.models import Link, Menu


class MenuFormTests(TestCase):
    def test_menu_addform(self):
        form_add = MenuAddForm({"title": "Testmenu1"})
        self.assertTrue(form_add.is_valid())

    def test_add_menu(self):
        menuaddurl = reverse("admin:menus_menu_add", args=[])
        response = self.client.post(menuaddurl, {"title": "Testmenu1"})
        self.assertTrue(response.status_code in (200, 302))

    def test_menuchildrenwidgets(self):
        menu = Menu.objects.add_root(title="Menu1")
        Menu.objects.add_child(
            parent=menu,
            title="l1",
            content_object=Link.objects.create(url="#1"),
        )
        data = menu.__dict__
        form_change = MenuChangeForm(data, instance=menu)
        self.assertTrue('value="l1"' in form_change.as_p())

    def test_dublicate_entry(self):
        menu = Menu.objects.add_root(title="Menu1")
        Menu.objects.add_child(
            parent=menu,
            title="l1",
            content_object=Link.objects.create(url="#1"),
        )
        Menu.objects.add_child(
            parent=menu,
            title="l2",
            content_object=Link.objects.create(url="#2"),
        )
        data = menu.__dict__
        data["entry-text-0"] = "a"
        data["entry-text-1"] = "a"
        form_change = MenuChangeForm(data, instance=menu)
        self.assertFalse(form_change.is_valid())

        data["entry-text-1"] = "b"
        form_change = MenuChangeForm(data, instance=menu)
        self.assertTrue(form_change.is_valid())
