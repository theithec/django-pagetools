from django.contrib.auth.models import User  # pylint: disable=imported-auth-user
from django.test import TestCase

from pagetools.pages.models import Page
from pagetools.settings import STATUS_PUBLISHED


class PageTests(TestCase):
    def setUp(self):
        self.username = "admin"
        self.email = "test@test.com"
        self.password = "test"
        self.admin = User.objects.create_superuser(self.username, self.email, self.password)
        self.admin.save()
        self.page = Page.objects.create(title="p1", slug="p1", included_form=list(Page.includable_forms.keys())[0])

    def test_title(self):
        self.assertEqual(self.page.title, "p1")

    def test_draft(self):
        self.assertEqual(self.page.status, "draft")
        resp = self.client.get(self.page.get_absolute_url())
        self.assertEqual(resp.status_code, 404)

    def test_draft_admin(self):
        self.assertEqual(self.page.status, "draft")
        self.client.login(username=self.username, password=self.password)
        resp = self.client.get(self.page.get_absolute_url())
        self.assertEqual(resp.status_code, 200)

    def test_published(self):
        self.page.status = STATUS_PUBLISHED
        self.page.save()
        resp = self.client.get(self.page.get_absolute_url())
        self.assertEqual(resp.status_code, 200)

    def tearDown(self):
        self.client.logout()
