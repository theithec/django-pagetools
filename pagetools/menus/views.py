from django.template.defaultfilters import slugify


class SelectedMenuentriesMixin:
    """Tries to find a slug from view or model add adds it to
    context. Used for find the selected menu-entries.
    """

    def get_context_data(self, *args, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        sel = kwargs.get("menukeys", [])
        sel.append(self.get_menukey())
        kwargs["menukeys"] = sel
        return kwargs

    def get_menukey(self):
        try:
            return self.get_object().slug
        except AttributeError:
            try:
                return self.menukey
            except AttributeError:
                return slugify(self.__class__.__name__.lower())

    # reduce queries
    def get_object(self, *args, **kwargs):
        if not getattr(self, "object", None):
            self.object = super().get_object()
        return self.object
