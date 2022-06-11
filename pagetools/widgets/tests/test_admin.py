from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.test.testcases import TestCase

from pagetools.utils import get_adminadd_url, get_adminedit_url
from pagetools.widgets.models import ContentWidget, PageType, TypeArea


class TypeAreaAdminTests(TestCase):
    def setUp(self):
        self.admin = get_user_model().objects.create_superuser("admin", "q@w.de", "password")
        self.client.login(username="admin", password="password")
        self.site = admin.sites.AdminSite()
        self.pagetype = PageType.objects.create(name="base")
        # self.typearea = TypeArea.objects.create(
        #    type=self.pagetype, area="sidebar")

    def _test_add_typearea(self):
        response = self.client.post(
            get_adminadd_url(TypeArea),
            {
                "pagetype": self.pagetype.pk,
                "area": "sidebar",
                "widgets-TOTAL_FORMS": 1,
                "widgets-INITIAL_FORMS": 0,
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)

    def _test_add_contentwidget(self):
        response = self.client.post(
            get_adminadd_url(ContentWidget),
            {
                "name": "name1",
                "content": "txt1",
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(ContentWidget.objects.filter(name="name1")), 1)

    def test_edit(self):
        self._test_add_typearea()
        self._test_add_contentwidget()
        typearea = TypeArea.objects.get(pagetype=self.pagetype, area="sidebar")
        adminurl = get_adminedit_url(typearea)
        response = self.client.get(adminurl)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(str(typearea), "sidebar_base")
        widget = ContentWidget.objects.get(name="name1")
        data = typearea.__dict__
        data.update(
            {
                "widgets-TOTAL_FORMS": 1,
                "widgets-INITIAL_FORMS": 0,
                # 'widgets-MAX_NUM_FORMS':1000,
                "add_objs": "%s_%s" % (ContentType.objects.get_for_model(widget).pk, widget.pk),
            }
        )
        response = self.client.post(adminurl, data, follow=True)
        self.assertEqual(response.status_code, 200)
