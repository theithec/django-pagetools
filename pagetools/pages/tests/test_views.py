from unittest import mock

import pagetools.pages.models
from pagetools.menus.tests import MenuDataTestCase
from pagetools.pages.forms import CaptchaContactForm


class PageViewTestCase(MenuDataTestCase):
    def test_detailview(self):
        response = self.client.get(self.page1.get_absolute_url())
        self.assertEqual(response.status_code, 200)  # type: ignore

    @mock.patch("pagetools.pages.forms.MAILFORM_RECEIVERS", ["q@w.de"])
    @mock.patch("captcha.conf.settings.CAPTCHA_TEST_MODE", True)
    def test_with_form(self):
        data = {
            "sender": "x@y.de",
            "name": "Name",
            "message": "The Message",
            "content": "Content",
            "subject": "Subject",
            "captcha_0": "PASSED",
            "captcha_1": "PASSED",
        }
        pagetools.pages.models.Page.includable_forms = {"Contactform": CaptchaContactForm}  # type: ignore
        response = self.client.post(self.page1.get_absolute_url(), data)
        self.assertEqual(response.status_code, 200, response.content)  # type: ignore
        self.assertNotContains(response, "An error occured")

        data.pop("sender")
        response = self.client.post(self.page1.get_absolute_url(), data)
        self.assertEqual(response.status_code, 200)  # type: ignore
        self.assertContains(response, "error_1_id_sender")
