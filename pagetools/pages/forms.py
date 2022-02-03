import logging
import os

from captcha.fields import CaptchaField
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.forms import widgets
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from pagetools.pages.validators import validate_emails_str
from pagetools.settings import SUBMIT_BUTTON_CLASSES

from .settings import MAILFORM_RECEIVERS, MAILFORM_SENDER


logger = logging.getLogger(__name__)


class DynMultipleChoiceField(forms.MultipleChoiceField):
    def __init__(self, **kwargs):
        try:
            label, values = kwargs["label"].split(":")
        except ValueError:
            raise ValidationError(_('ChoiceField name must be "name: option1, option2 [...])'))
        kwargs.update(
            {
                "label": label,
                "choices": [(slugify(v), v) for v in values.split(",")],
                "widget": widgets.CheckboxSelectMultiple,
            }
        )
        super(DynMultipleChoiceField, self).__init__(**kwargs)


class SendEmailForm(forms.Form):

    IGNORED_FIELDS_IN_MESSAGE = ("captcha",)
    USE_MAILRECEIVERS = True

    def __init__(self, *args, **kwargs):
        self.mailreceivers = kwargs.pop("mailreceivers", None) or MAILFORM_RECEIVERS
        super(SendEmailForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.add_input(Submit("submit", _("Submit"), css_class=SUBMIT_BUTTON_CLASSES))

    def get_mailmessage(self):
        return os.linesep.join(
            [
                "%s\t%s" % (field.name, field.value())
                for field in self
                if field.name not in self.IGNORED_FIELDS_IN_MESSAGE
            ]
        )

    def get_mailsubject(self):
        return _("Form submission")

    def get_mailreceivers(self):
        return self.mailreceivers

    def get_mailsender(self):
        return MAILFORM_SENDER

    def is_valid(self):
        _is_valid = super(SendEmailForm, self).is_valid()
        if _is_valid:
            send_mail(
                self.get_mailsubject(),
                self.get_mailmessage(),
                self.get_mailsender(),
                self.get_mailreceivers(),
                fail_silently=False,
            )
        return _is_valid

    def clean(self):
        super(SendEmailForm, self).clean()
        if not self.mailreceivers:
            raise ValidationError(_("An error occured"))
        validate_emails_str(",".join(self.mailreceivers))

    def get_error_msg(self):
        return _("An error occured")


class ContactForm(SendEmailForm):
    subject = forms.CharField(max_length=100, label=_("About"), required=True)
    name = forms.CharField(label=_("Your Name"))
    sender = forms.EmailField(label=_("E-Mail"))
    message = forms.CharField(widget=forms.widgets.Textarea(), label=_("Message"))


class CaptchaContactForm(ContactForm):
    captcha = CaptchaField()
