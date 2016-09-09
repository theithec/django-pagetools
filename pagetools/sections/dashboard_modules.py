from django.utils.html import format_html
from grappelli.dashboard.modules import DashboardModule


class PageNodesModule(DashboardModule):
    """
    A module that displays a page with nodes.
    A "page" should be the root-pagenode model.
    Overwrite model =  <YourModel>

    Dashboard needs to include the static files, e.g:
    ----------------------------------------------------------------------------
    from django import forms
    ...
    def _media(self):
            return forms.Media(
                js=["bower_components/jquery/dist/jquery.min.js",
                    "bower_components/jquery-bonsai/jquery.bonsai.js",
                    "js/nodetree.js"
                    ],
                css = {'all': [
                'bower_components/jquery-bonsai/jquery.bonsai.css ']}
            )

    media = property(_media)

    urls.py:
        url(
            r'^adminnodes/(?P<slug>[\w-]+)/$',
            admin_pagenodesview,
            name='admin_pagenodesview'),
    ----------------------------------------------------------------------------

    """

    template = 'admin/dashboard_pagenodes_module.html'
    model = None

    def __init__(self, *args, **kwargs):
        kwargs['title'] = "Nodes Tree"
        self.model = kwargs.pop('model')
        super().__init__(*args, **kwargs)

    def init_with_context(self, context):
        pages = self.model.objects.filter(
            content_type_pk=self.model.get_contenttype_pk())
        context['pages'] = pages
        context['admin_pagenodesview'] = '/adminnodes/__SLUG__'
        options = ""
        for p in pages:
            options += format_html(
                '<option name={}>{}</option>', p.slug, p.title)
        self.pre_content = '''<label>
            Page
            </label>
            <select style="width: auto;" id='pagenode_page_chooser'>
                %s
            </select>''' % options

        super(PageNodesModule, self).init_with_context(context)
        self._initialized = True
