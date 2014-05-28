'''
Created on 01.01.2014

@author: lotek
'''

from django import forms
from django.utils.translation import get_language, ugettext_lazy as _
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from . import search_mods
from pagetools.core.utils import get_classname


class AdvSearchForm(forms.Form):
    contains_all = forms.CharField(label=_('contains all'), required=False)
    contains_any = forms.CharField(label=_('contains any'), required=False)
    contains_exact = forms.CharField(label=_('contains exact'), required=False)
    contains_not = forms.CharField(label=_('contains not '), required=False)

    def __init__(self, *args, **kwargs):
        super(AdvSearchForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'get'
        self.helper.add_input(Submit('submit', 'Submit'))

        _models = []
        for k, v in search_mods:
            _models.append(k)
        choices = [('%s' % i, get_classname(k)) for i, k in enumerate(_models)]
        self.fields['models'] = forms.MultipleChoiceField(choices=choices,
                                                          required=False)