# coding=utf-8
import json
import logging

from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.views.generic import (View, CreateView, UpdateView,
                                  DeleteView, DetailView, ListView)
from django.contrib.auth.views import logout
from django.views.decorators.cache import never_cache
from common.exceptions import InvalidParameters
from common.forms.utils import form_errors_to_list
from common.mixin import JSONResponseMixin
from identity.models import Permission, Resource
from identity.forms import *
from identity.views.resources import resource_detail

User = get_user_model()
logger = logging.getLogger('default')


# Create your views here.


class Login(auth_views.LoginView):

    template_name = 'identity/authentication/login.html'
    # redirect_field_name = 'next'  # default
    authentication_form = AuthenticationForm
    redirect_authenticated_user = True

    # A dictionary of context data that will be added to
    # the default context data passed to the template.
    extra_context = {}
    initial = {'key': 'value'}

    def get(self, request, *args, **kwargs):
        logger.debug('login page')
        form = self.authentication_form(initial=self.initial, auto_id=True)
        self.extra_context.update(
            {'form': form,
             'next': self.request.GET.get('next', '')}
        )
        return render(request, self.template_name, self.extra_context)

    def post(self, request, *args, **kwargs):
        context = {}
        form = self.authentication_form(data=request.POST, auto_id=True,
                                        error_class=DivErrorList)
        if form.is_valid():
            username = form.cleaned_data['username']

            # do something here
            context['username'] = username
            user = User.objects.get(username=username)

            # log into
            login(request, user)

            remember_me = form.cleaned_data['remember_me']
            if not remember_me:
                # session will expire on closing browser
                request.session.set_expiry(0)

            messages.add_message(request, messages.SUCCESS,
                                 'Welcome, %s' % username)
            return HttpResponseRedirect(self.get_success_url())
        else:
            return render(request, self.template_name, {'form': form})


class Logout(JSONResponseMixin, auth_views.LogoutView):

    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        try:
            logout(request)
        except Exception as e:
            logger.error('logout error, %s' % str(e))
            return self.render_to_json_response(result=False, messages=_(
                'An error occurred when logged out'))
        next_page = self.get_next_page()
        if next_page:
            # Redirect to this page until the session has been cleared.
            messages.add_message(request, messages.SUCCESS,
                                 _('You have successfully logged out'))
            return self.render_to_json_response(default_msg=False)
        return super().dispatch(request, *args, **kwargs)


@method_decorator(login_required, name='dispatch')
class UserCreate(JSONResponseMixin, PermissionRequiredMixin, CreateView):

    permission_required = 'identity.create_user'
    raise_exception = True
    form_class = UserCreationForm
    model = User

    def post(self, request, *args, **kwargs):
        form = self.form_class(data=request.POST, auto_id=True,
                               error_class=DivErrorList)
        if form.is_valid():
            username = form.cleaned_data['username']
            self.model().create_user(
                username,
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password1']
            )
            return self.render_to_json_response(
                messages=_('User %s has been successfully created.' % username),
                data=self.model.objects.all().values('id', 'username', 'email',
                                                     'date_joined', 'last_login'))
        else:
            return self.render_to_json_response(
                result=False, messages=form_errors_to_list(form.errors))


@method_decorator(login_required, name='dispatch')
class UserUpdate(PermissionRequiredMixin, JSONResponseMixin, UpdateView):

    permission_required = 'identity.update_user'
    raise_exception = True
    model = User
    form_class = UserUpdateForm
    pk_url_kwarg = 'user_id'

    def post(self, request, *args, **kwargs):
        form = self.form_class(data=request.POST, error_class=DivErrorList)
        if form.is_valid():
            user_obj = self.get_object()
            user_obj.email = request.POST.get('email')
            user_obj.save()
            return self.render_to_json_response(data={'email': user_obj.email})
        else:
            raise self.render_to_json_response(result=False)


@method_decorator(login_required, name='dispatch')
class UserDelete(PermissionRequiredMixin, DeleteView):

    permission_required = 'identity.delete_user'
    raise_exception = True
    model = User
    pk_url_kwarg = 'user_id'
    success_url = '/identity/user/'


@method_decorator(login_required, name='dispatch')
class UserDetail(PermissionRequiredMixin, DetailView):

    permission_required = 'identity.detail_user'
    raise_exception = True
    model = User
    template_name = 'identity/management/user_detail.html'
    pk_url_kwarg = 'user_id'

    extra_context = {}

    def get_context_data(self, **kwargs):
        # rendering user's global permission modal
        all_perms = Permission.objects.all()
        cts = list()
        res = list()

        global_perms = self.object.user_permissions.all()
        global_perms_id_list = [item.id for item in global_perms]

        for ap in all_perms:
            if ap.content_type_id not in cts:
                cts.append(ap.content_type_id)
                res.append(
                    {'id': ap.content_type_id,
                     'name': ap.content_type.name})
            if ap.id in global_perms_id_list:
                ap.assigned = True
            else:
                ap.assigned = False

        # user's object permission modal
        user_resources = self.object.get_resources()
        format_resources = {}   # format resources to a dict category by type
        for r in user_resources:
            if format_resources.get(r.type) is None:
                format_resources[r.type] = [resource_detail(r)]
            else:
                format_resources[r.type].append(resource_detail(r))
        user_resource_ids = [i.id for i in user_resources]

        format_not_resources = {}
        not_user_resources = Resource.objects.exclude(id__in=user_resource_ids)
        for r in not_user_resources:
            if format_not_resources.get(r.type) is None:
                format_not_resources[r.type] = [resource_detail(r)]
            else:
                format_not_resources[r.type].append(resource_detail(r))

        kwargs.update({'all_perms': all_perms,
                       'format_not_resources': format_not_resources,
                       'format_resources': format_resources,
                       'resources': user_resources,
                       'perm_content_types': res,
                       'user_update_form': UserUpdateForm})
        return super().get_context_data(**kwargs)


@method_decorator(login_required, name='dispatch')
class UserList(PermissionRequiredMixin, ListView):

    permission_required = 'identity.list_user'
    raise_exception = True
    model = User
    template_name = 'identity/management/user_list.html'

    def get_queryset(self):
        return self.model.objects.all()

    def get_context_data(self, *, object_list=None, **kwargs):
        kwargs.update({'user_create_form': UserCreationForm()})
        return super().get_context_data(**kwargs)


@method_decorator(login_required, name='dispatch')
class UserPermissionUpdate(PermissionRequiredMixin, JSONResponseMixin, UpdateView):

    permission_required = 'identitiy.update_user_permission'
    raise_exception = True
    model = User
    pk_url_kwarg = 'user_id'

    def post(self, request, *args, **kwargs):
        obj = get_object_or_404(self.model, pk=kwargs.get(self.pk_url_kwarg))

        # permission id list
        new_perms = request.POST.get('checked_perms')
        if not new_perms:
            raise InvalidParameters
        try:
            checked_perms = json.loads(new_perms)
        except json.JSONDecodeError:
            raise InvalidParameters

        checked_perms = [item for item in checked_perms if item.isdigit()]
        old_perms_id_list = [str(i.id) for i in obj.user_permissions.all()]

        for oid in old_perms_id_list:
            if oid not in checked_perms:
                # delete
                obj.user_permissions.remove(oid)

        for nid in checked_perms:
            if nid not in old_perms_id_list:
                # add
                obj.user_permissions.add(nid)

        return self.render_to_json_response()


@method_decorator(login_required, name='dispatch')
class PasswordChange(auth_views.PasswordChangeView):
    """
    Change password by providing current password
    """

    template_name = 'identity/authentication/password_change.html'


@method_decorator(login_required, name='dispatch')
class PasswordChangeDone(auth_views.PasswordChangeDoneView):
    """
    Change password done
    """
    template_name = 'identity/authentication/password_change_done.html'


@method_decorator(login_required, name='dispatch')
class PasswordReset(auth_views.PasswordResetView):
    """
    Validate and send a password reset email
    """
    pass


@method_decorator(login_required, name='dispatch')
class PasswordResetDone(auth_views.PasswordResetDoneView):
    """
    Email has been sent
    """
    pass


@method_decorator(login_required, name='dispatch')
class PasswordResetConfirm(auth_views.PasswordResetConfirmView):
    """
    Authorized to set a new password
    """
    pass


@method_decorator(login_required, name='dispatch')
class PasswordResetComplete(auth_views.PasswordResetCompleteView):
    """
    Password reset all done
    """
    pass