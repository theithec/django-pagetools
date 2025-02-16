from pagetools.menus.utils import get_menukey


class SelectedMenuentriesMixin:
    """Tries to find a slug from view or model add adds it to
    context. Used for find the selected menu-entries.
    """
    menukey: str

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        menukey = kwargs.get("menukey", getattr(self, "menukey", None))
        if not menukey:
            menukey = get_menukey(self.get_object())
        kwargs["menukey"] = menukey
        print("\nMK", kwargs["menukey"])
        return kwargs
            

    def get_object(self, *args, **kwargs):
        if not getattr(self, "object", None):
            try:
                self.object = super().get_object()
            except AttributeError:
                self.object = self
        print("VIEW GO", self, self.object)
        return self.object
