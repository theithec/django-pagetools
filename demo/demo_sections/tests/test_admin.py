from django.contrib.auth.models import User
from pagetools.core.utils import get_adminadd_url, get_adminedit_url

from demo_sections.models import Article, SectionList
from demo_sections.tests import SectionsDataTestCase
import pagetools.sections.dashboard_modules

class AdminTest(SectionsDataTestCase):

    def setUp(self):
        self.admin = User.objects.create_superuser('admin', 'q@w.de', 'password')
        self.client.login(username="admin", password='password')
        super().setUp()

    def test_article_add(self):
        response = self.client.get(get_adminadd_url(Article))
        self.assertTrue(response.status_code, 200)

    def test_article_edit(self):
        response = self.client.get(get_adminedit_url(self.articles[0]))
        self.assertTrue(response.status_code, 200)

    def test_sectionlist_edit(self):
        response = self.client.get(get_adminedit_url(self.sectionlist1))
        self.assertTrue(response.status_code, 200)

    def test_adminnodeview(self):
        pagetools.sections.dashboard_modules.PageNodesModule.model = SectionList
        #  print("ALL", SectionList.objects.all())
        response = self.client.get(
            '/adminnodes/%s/' % self.sectionlist1.slug,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        # self.assertTrue(str(response.content).startswith("<ol"))
        self.assertTrue(response.status_code, 200)

