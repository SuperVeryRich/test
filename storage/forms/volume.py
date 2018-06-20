from django import forms
from common.models import get_resource_model
from django.utils.translation import ugettext_lazy as _
from .helper import get_user_choices, get_storage_choices

Resource = get_resource_model()


class VolumeCreationForm(forms.Form):
    """
    创建用户
    """
    name = forms.CharField(
        label=_('Name'),
        max_length=32,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'id': 'volume-name-input',
                'required': True,
                'spellcheck': 'false',
                'autofocus': 'autofocus',
            }
        ),
    )
    size = forms.IntegerField(
        label=_('Size'),
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'id': 'volume-capacity-input',
                'value': 1,
                'required': True,
            }
        ),
    )
    number = forms.IntegerField(
        label=_('Number'),
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'id': 'volume-number-input',
                'value': 1,
                'required': True,
            }
        ),
    )
    user = forms.ChoiceField(
        label=_('User'),
        choices=get_user_choices(),
        widget=forms.Select(
            attrs={
                'class': 'form-control',
                'id': 'volume-user-select',
                'required': True,
            }
        ),
    )
    storage = forms.ChoiceField(
        label=_('Storage'),
        choices=get_storage_choices(),
        widget=forms.Select(
            attrs={
                'class': 'form-control',
                'id': 'volume-storage-select',
                'required': True,
            }
        ),
    )
