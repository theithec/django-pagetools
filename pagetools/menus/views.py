from pagetools.menus.utils import get_menukey


class SelectedMenuentriesMixin:
    """Tries to find a slug from view or model add adds it to
    context. Used for find the selected menu-entries.
    """

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        sel = kwargs.get("menukeys", [])
        sel.append(self.get_menukey())
        kwargs["menukeys"] = sel
        return kwargs

    def get_menukey(self):
        try:
            obj = self.get_object()
        except AttributeError:
            obj = self
        return get_menukey(obj)

    # reduce queries
    def get_object(self, *args, **kwargs):
        if not getattr(self, "object", None):
            self.object = super().get_object()
        return self.object
