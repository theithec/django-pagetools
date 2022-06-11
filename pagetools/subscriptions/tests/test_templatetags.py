from unittest import mock

from django.test import TestCase

from pagetools.subscriptions.templatetags.subscriptions_tags import do_subscribe_node


class TemplateTagTestCase(TestCase):
    def test_subscripton_node(self):
        nsn = do_subscribe_node(mock.Mock(), mock.Mock())
        request = mock.MagicMock()
        request.META = {}
        self.assertTrue('name="email"' in nsn.render({"request": request}))
