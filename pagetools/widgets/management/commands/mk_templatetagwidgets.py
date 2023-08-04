from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _

from pagetools.widgets.models import TemplateTagWidget
from pagetools.widgets.settings import TEMPLATETAG_WIDGETS


class Command(BaseCommand):
    help = _("create Widgets according to settings.(PT_)TEMPLATETAG_WIDGETS ")

    def handle(self, *args, **options):
        for key in list(TEMPLATETAG_WIDGETS.keys()):
            ttw = TemplateTagWidget.objects.create(
                name=key,
                renderclasskey=key,
            )
            print(("created: %s" % ttw))
