from django.test import TestCase

from pagetools.utils import get_classname


class Verbose:
    class _meta:
        verbose_name = "Bar"


class NonVerbose:
    pass


class UtilTest(TestCase):
    def test_get_verbose_classname(self):
        self.assertEqual(get_classname(Verbose), "Bar")

    def test_get_nonverbose_classname(self):
        self.assertEqual(get_classname(NonVerbose), "NonVerbose")
