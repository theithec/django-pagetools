"""
This file was generated with the customdashboard management command and
contains the class for the main dashboard.

To activate your index dashboard add the following to your settings.py::
    GRAPPELLI_INDEX_DASHBOARD = 'demo.dashboard.CustomIndexDashboard'
"""
from demo_sections.models import SectionList
from django import forms
from django.utils.translation import gettext_lazy as _
from grappelli.dashboard import Dashboard, modules

from pagetools.menus.dashboard_modules import MenuModule
from pagetools.sections.dashboard_modules import PageNodesModule


PageNodesModule.model = SectionList


class CustomIndexDashboard(Dashboard):
    """
    Custom index dashboard for www.
    """

    def init_with_context(self, context):
        # site_name = get_admin_site_name(context)
        self.children.append(MenuModule(column=1))
        self.children.append(PageNodesModule(model=SectionList, column=1))

        # append an app list module for "Applications"
        self.children.append(
            modules.AppList(
                _("AppList: Applications"),
                collapsible=True,
                column=1,
                css_classes=("collapse closed",),
                exclude=("django.contrib.*",),
            )
        )

        # append an app list module for "Administration"
        self.children.append(
            modules.ModelList(
                _("ModelList: Administration"),
                column=1,
                collapsible=False,
                models=("django.contrib.*",),
            )
        )

        # append another link list module for "support".
        self.children.append(
            modules.LinkList(
                _("Media Management"),
                column=2,
                children=[
                    {
                        "title": _("FileBrowser"),
                        "url": "/admin/filebrowser/browse/",
                        "external": False,
                    },
                ],
            )
        )

        # append another link list module for "support".
        self.children.append(
            modules.LinkList(
                _("Support"),
                column=2,
                children=[
                    {
                        "title": _("Django Documentation"),
                        "url": "http://docs.djangoproject.com/",
                        "external": True,
                    },
                    {
                        "title": _("Grappelli Documentation"),
                        "url": "http://packages.python.org/django-grappelli/",
                        "external": True,
                    },
                    {
                        "title": _("Grappelli Google-Code"),
                        "url": "http://code.google.com/p/django-grappelli/",
                        "external": True,
                    },
                ],
            )
        )

        # append a feed module
        self.children.append(
            modules.Feed(
                _("Latest Django News"),
                column=2,
                feed_url="http://www.djangoproject.com/rss/weblog/",
                limit=5,
            )
        )

        # append a recent actions module
        self.children.append(
            modules.RecentActions(
                _("Recent Actions"),
                limit=5,
                collapsible=False,
                column=3,
            )
        )

    def _media(self):
        return forms.Media(
            js=[
                "bower_components/jquery/dist/jquery.min.js",
                "bower_components/jquery-bonsai/jquery.bonsai.js",
                "js/nodetree.js",
            ],
            css={"all": ["bower_components/jquery-bonsai/jquery.bonsai.css"]},
        )

    media = property(_media)
