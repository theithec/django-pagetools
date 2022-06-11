from django.test import TestCase

from pagetools.sections.models import PageNode


class TestModelMixin(TestCase):
    def setUp(self):

        self.model = PageNode
        self.node1 = self.model.objects.create(title="w1")


class ModelTests(TestModelMixin):
    def test_title(self):
        self.assertEqual(self.node1.title, "w1")
