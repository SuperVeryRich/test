# coding=utf-8
import re
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import forms as auth_forms
from django.forms.utils import ErrorList
from django.contrib.auth import get_user_model
from identity.models import User


__all__ = [
    'AuthenticationForm',
    'UserCreationForm',
    'UserUpdateForm',
    'PasswordChangeForm',
    'GroupCreateForm',
    'GroupUpdateForm',
]


class AuthenticationForm(auth_forms.AuthenticationForm):
    """
    用户登录验证
    """

    def __init__(self, *args, **kwargs):
        super(AuthenticationForm, self).__init__(*args, **kwargs)

    error_css_class = 'error'
    required_css_class = 'required'

    # email = forms.EmailField(
    #     widget=forms.EmailInput(attrs={'class': 'validate'}),
    #     max_length=32,
    #     min_length=6
    # )
    username = auth_forms.UsernameField(
        label=_('Username'),
        max_length=32,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'id': 'login-input-username',
                'placeholder': _('Username'),
                'required': True,
                'spellcheck': 'false',
                'autofocus': 'autofocus',
            }
        ),
    )
    password = forms.CharField(
        label=_('Password'),
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'id': 'login-input-password',
                'placeholder': _('Password'),
                'maxlength': 32,
                'minlength': 8,
                'required': True
            }
        ),
    )
    password_length = forms.IntegerField(
        widget=forms.HiddenInput(),
        max_value=32,
        min_value=8,
        required=False
    )
    remember_me = forms.BooleanField(
        label=_('Remember me'),
        label_suffix='',  # remove ':'
        widget=forms.CheckboxInput(
            attrs={'id': 'remember_me'}
        ),
        required=False,
    )

    def clean_username(self):
        # Just an example of cleaning a specific filed attribute
        # cleaned_data = super(LoginForm, self).clean()
        username = self.cleaned_data['username']
        for i in '!@#$%^&*':
            if i in username:
                raise forms.ValidationError
        return username

    def confirm_login_allowed(self, user):
        # allow inactive user to login
        pass


class UserCreationForm(auth_forms.UserCreationForm):
    """
    创建用户
    """
    username = auth_forms.UsernameField(
        label=_('Username'),
        max_length=32,
        widget=forms.TextInput(
            attrs={
                'id': 'user-create-input-name',
                'class': 'form-control',
                'autofocus': True,
                'required': True,
                'placeholder': _('Username')
            }
        ),
        help_text=_('Enter your username.')
    )
    password1 = forms.CharField(
        label=_('Password'),
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                'id': 'user-create-input-password1',
                'class': 'form-control',
                'maxlength': 32,
                'minlength': 8,
                'required': True,
                'placeholder': _('Password')
            }
        ),
        help_text=_('Enter your password.')
    )
    password2 = forms.CharField(
        label=_('Password confirm'),
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                'id': 'user-create-input-password2',
                'class': 'form-control',
                'maxlength': 32,
                'minlength': 8,
                'required': True,
                'placeholder': _('Password confirm')
            }
        ),
        help_text=_('Enter the same password as before, for verification.')
    )
    email = forms.EmailField(
        label=_('Email address'),
        widget=forms.EmailInput(
            attrs={
                'id': 'user-create-input-email',
                'class': 'form-control',
                'max_length': 64,
                'min_length': 8,
                'required': True,
                'placeholder': _('Email')
            }
        ),
        help_text=_('Enter your email address.')
    )
    password_length = forms.IntegerField(
        widget=forms.HiddenInput(),
        max_value=32,
        min_value=8,
        required=False
    )

    class Meta:
        model = get_user_model()
        fields = ("username",)

    def clean_username(self):
        # Just an example of cleaning a specific filed attribute
        # cleaned_data = super(LoginForm, self).clean()
        username = self.cleaned_data['username']

        if not re.match('^\w+$', username):
            self.add_error('username',
                           'Enter a valid username. This value may contain '
                           'only letters, numbers, and _ characters.')
        return username


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(
                attrs={
                    'id': 'user-update-input-password',
                    'class': 'form-control',
                    'max_length': 64,
                    'min_length': 8,
                    'required': True,
                    'placeholder': _('Email')
                }
            )
        }
        labels = {
            'email': _('Email address')
        }
        help_texts = {
            'email': _('Input your email address.'),
        }
        # error_messages = {
        #     'email': {
        #         'max_length': _("This writer's name is too long."),
        #     },
        # }

    def clean_email(self):
        # custom clean method
        email = self.cleaned_data['email']
        if email.startswith('admin'):
            raise forms.ValidationError


class PasswordChangeForm(auth_forms.PasswordChangeForm):
    """
    修改密码
    """
    pass


class GroupCreateForm(forms.Form):

    name = forms.CharField(
        label=_('Group name'),
        strip=False,
        widget=forms.TextInput(
            attrs={
                'id': 'group-create-input-name',
                'class': 'form-control',
                'maxlength': 80,
                'required': True,
                'placeholder': _('Group name')
            }
        ),
    )


class GroupUpdateForm(forms.Form):
    """
    把用户加入到(移除出)组
    """
    groups = forms.ChoiceField()
