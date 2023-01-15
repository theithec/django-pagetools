from demo_sections.tests import SectionsDataTestCase
from django.urls import reverse

from pagetools.menus.models import ViewLink
from pagetools.menus.tests import MenuDataTestCase


class Views1Test(SectionsDataTestCase):
    def test_view(self):
        response = self.client.get(self.sectionlist1.get_absolute_url())
        self.assertEqual(response.status_code, 200)

    def test_ajaxview(self):
        response = self.client.get(
            reverse(
                "sections:ajax",
                kwargs={
                    "slug": self.articles[0].slug,
                },
            ),
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        self.assertEqual(response.status_code, 200)


class Views2Test(MenuDataTestCase):
    def test_questionlist(self):
        vlink = ViewLink.objects.create(name="polls:index")
        self.menu.children.add_child(parent=self.menu, content_object=vlink, title="Polls", enabled=True)
        response = self.client.get(reverse("polls:index"))

        self.assertEqual(response.status_code, 200)
