from django.conf import settings
from django.test import TestCase
from django.test.client import Client
from django.urls import reverse
from django.utils.text import slugify

import pagetools.search
import pagetools.search.views
from pagetools.pages.models import Page
from pagetools.settings import STATUS_PUBLISHED


pagetools.search.search_mods = [
    (Page, ("title", "content"), {"replacements": "content"}),
]
pagetools.search.views.SearchResultsView._search_mods = pagetools.search.search_mods  # pylint: disable=protected-access
pagetools.search.extra_filter = lambda x: x.filter(status=STATUS_PUBLISHED)
pagetools.search.views.extra_filter = lambda x: x.filter(status=STATUS_PUBLISHED)


class SearchViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        for title, content, is_pub in [("P%s" % i, "Foo%s" % i, True) for i in range(4)]:
            Page.objects.create(
                **{
                    "title": title,
                    "content": content,
                    "slug": slugify(title),
                    "status": "published" if is_pub else "draft",
                }
            )

            settings.PAGINATE_BY = 3

    def test_search4page(self):
        response = self.client.get(reverse("search") + "?contains_all=Foo1")
        self.assertTrue("P1" in str(response.content))
        self.assertFalse("P2" in str(response.content))

        page2 = Page.objects.get(title="P2")
        page2.status = "draft"
        page2.save()

        response = self.client.get("/search/?contains_any=Foo1 Foo2")
        self.assertTrue("P1" in str(response.content))
        self.assertFalse("P2" in str(response.content))
        self.assertFalse("P3" in str(response.content))
