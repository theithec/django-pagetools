from pagetools.menus.utils import get_menukey

from .apps import MenusConfig

class SelectedMenuentriesMixin:
    """Tries to find a menukey from view or model add adds it to
    context. Used for find the selected menu-entries.
    """

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        kwargs["menukey"] = get_menukey(self.get_object(), **kwargs)
        return kwargs

    def get_object(self, *args, **kwargs):
        if not getattr(self, "object", None):
            try:
                self.object = super().get_object()
            except AttributeError:
                self.object = self
        return self.object


    def get_menukey(self):   
        rmatch = self.request.resolver_match
        parts = rmatch.namespaces + [rmatch.url_name]
        return ":".join(filter(None, parts))