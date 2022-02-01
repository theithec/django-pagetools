from django.core.management import call_command
from django.test import TestCase

from pagetools.widgets.models import TemplateTagWidget
from pagetools.widgets.settings import TEMPLATETAG_WIDGETS


class CommandsTestCase(TestCase):
    def test_mycommand(self):
        "Test my custom command."

        args = []
        opts = {}
        call_command("mk_templatetagwidgets", *args, **opts)
        widgetobjects = TemplateTagWidget.objects.all()
        self.assertEqual(len(TEMPLATETAG_WIDGETS), len(widgetobjects))
