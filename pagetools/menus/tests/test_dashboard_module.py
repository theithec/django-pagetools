from django.urls import reverse

from pagetools.menus.dashboard_modules import MenuModule
from pagetools.menus.tests import MenuDataTestCase


class DashboardTests(MenuDataTestCase):
    def setUp(self):
        super().setUp()
        self.module = MenuModule(menu_title=self.menu.title)

    def test_admin_index(self):
        """test index because customdashboard with MenuModule is may used"""
        adminindex = reverse("admin:index", args=[])
        response = self.client.get(adminindex, {})
        self.assertTrue(response.status_code in (200, 302))

    def test_add_entrychildren(self):
        context = {}
        self.module.init_with_context(context)
        self.assertEqual(sorted(context.keys()), sorted(("existing", "menu")))
        self.assertEqual(len(context["existing"]), 3)
