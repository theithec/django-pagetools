"""
A :class:`pagetools.pages.models.Page` (or abstract :class:`pagetools.pages.models.BasePage`)
inherits from :ref:`Pagelike` and adds

- a “included_form” field, which consists of the Forms defined in the includable_forms attribute of the Model.

- an “email_receivers” field which is only used if the selected an pagetools.pages.forms.SendEmailForm or a subclass.

- a foreign key to :class:`pagetools.widgets.models.PageType` (See :ref:`widgets`)

- a boolean field "login_required"


The :class:`pagetools.pages.views.PageView` knows how to handle these attribues through its baseclasses/mixins.
"""
