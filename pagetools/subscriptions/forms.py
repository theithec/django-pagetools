from django.utils.translation import ugettext_lazy as _
from django import forms
from django.urls import reverse

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from pagetools.settings import SUBMIT_BUTTON_CLASSES


class SubscribeForm(forms.Form):
    email = forms.EmailField(label=_("E-Mail"))

    def __init__(self, *args, **kwargs):
        super(SubscribeForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = "subscribeform"
        self.helper.form_action = reverse("subscriptions:subscribe")
        self.helper.add_input(
            Submit("subscribe", _("Submit"), css_class=SUBMIT_BUTTON_CLASSES)
        )
        self.helper.form_tag = True
