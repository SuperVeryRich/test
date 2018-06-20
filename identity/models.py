# coding=utf-8
from django.contrib.auth import get_user_model
from django.contrib.auth.models import (AbstractUser, BaseUserManager,
                                        Group, Permission)
from django.contrib.auth.validators import ASCIIUsernameValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from common.constants.resources import *
from common.models import Instances, Volumes, ComputeNodes, Storage
from common.utils.text_ import UUID, obj2iter

# Create your models here.


class UserManager(BaseUserManager):

    use_in_migrations = True

    def _create_user(self, username, email, password, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        """
        if not username:
            raise ValueError('The given username must be set')
        email = self.normalize_email(email)
        self.model = get_user_model()
        username = self.model.normalize_username(username)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('id', UUID.uuid4)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(username, email, password, **extra_fields)

    def create_superuser(self, username, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(username, email, password, **extra_fields)


class ResourceMixin:
    """
    User resource management
    """

    @staticmethod
    def _get_resources_detail(resources, resource_type):
        resource_ids = [r.id for r in resources]
        if resource_type == VOLUME:
            resources = Volumes.objects.filter(deleted=0, id__in=resource_ids)
        elif resource_type == SERVER:
            resource_ids = [r.uuid for r in resources]
            servers = Instances.objects.filter(deleted=0)
            resources = servers.filter(deleted=0, uuid__in=resource_ids)
        elif resource_type == HOST:
            hosts = ComputeNodes.objects.filter(deleted=0)
            resources = hosts.filter(deleted=0, id__in=resource_ids)
        elif resource_type == STORAGE:
            resource_ids = [r.id for r in resources]
            resources = Storage.objects.filter(id__in=resource_ids)
        elif resource_type == NETWORK:
            raise NotImplemented
        else:
            # TODO: more types
            raise ValueError
        return resources

    def has_resource(self, resource_id):
        return Resource.objects.filter(id=resource_id, user=self).exists()

    def get_resources(self, detail=False, reverse=False):
        """
        Get overall resources (or details)
        :param detail: True, return a dict object like {'volume': <QuerySet>, ...},
        else return a Resource object
        :param reverse: True, return the user's resources ,
        else return other user's resources
        :return:
        """
        if reverse:
            resources = Resource.objects.exclude(user=self)
        else:
            resources = Resource.objects.filter(user=self)
        if detail:
            types = list({}.fromkeys([i['type'] for i in resources if i.get('type')]).keys())
            types = filter(lambda x: x in ALL_RESOURCES, types)
            detail_result = {}
            for t in types:
                detail_result[t] = self._get_resources_detail(resources, t)
            return detail_result
        return resources

    def get_resources_by_type(self, resource_type, detail=False):
        """Get user resource by specified type"""
        resources = Resource.objects.filter(user=self, type=resource_type)
        if resources and detail:
            resources = self._get_resources_detail(resources, resource_type)
        return resources

    def get_resources_by_id(self, resource_id, detail=False):
        """Get user resource by specified id"""

        resources = Resource.objects.filter(user=self, id=resource_id)
        if resources and detail:
            resources = self._get_resources_detail(resources, resources[0].type)
        return resources

    def assign_resource(self, resource_id, resource_type):
        obj = Resource.objects.filter(id=resource_id)
        if obj.exists():
            obj.update(user=self)
        else:
            Resource.objects.create(id=resource_id,
                                    type=resource_type,
                                    user=self)

    def delete_resource(self, resource_id):
        Resource.objects.get(pk=resource_id, user=self).delete()

    def undo_assign_resource(self, resource_ids=None):
        """
        Remove resource(s) assignment from a user
        :param resource_ids: [list|tuple|None]
        :return:
        """
        if resource_ids:
            assert isinstance(resource_ids, (list, tuple, str))
            Resource.objects.filter(id__in=obj2iter(resource_ids)).update(user_id=None)
        else:
            Resource.objects.filter(user=self).update(user_id=None)


class Project(models.Model):
    """
    需要和keystone的tenant/project保持一致
    """

    id = models.CharField(max_length=36, verbose_name='id', primary_key=True)

    def __str__(self):
        return self.id

    class Meta:
        db_table = 'auth_project'
        default_permissions = ()


class User(ResourceMixin, AbstractUser, UserManager):
    """
    Custom user model
    """
    username_validator = ASCIIUsernameValidator()
    id = models.CharField(
        _('id'),
        max_length=36,
        primary_key=True,
        unique=True)
    groups = models.ManyToManyField(
        Group)
    user_permissions = models.ManyToManyField(
        Permission)

    username = models.CharField(
        _('username'),
        max_length=32,
        unique=True,
        help_text=_(
            'Required. 150 characters or fewer. '
            'Letters, digits and @/./+/-/_ only.'),
        validators=[username_validator],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )
    email = models.EmailField(_('email address'), blank=True)
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    # project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True)

    objects = UserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        db_table = 'auth_user'
        ordering = ['username']
        verbose_name = _('user')
        verbose_name_plural = _('users')
        permissions = (
            ('list_user', _('Can see user list')),
            ('detail_user', _('Can see user detail')),
            ('create_user', _('Can create user')),
            ('update_user', _('Can update user')),
            ('delete_user', _('Can delete user')),
            ('update_user_permission', _('Can update user permission')),
            ('update_user_group', _('Can update user group'))
        )
        default_permissions = ()

    def __str__(self):
        return self.username

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def delete(self, using=None, keep_parents=False):
        # need to remove user's resources first
        self.undo_assign_resource()
        super().delete(using=using, keep_parents=keep_parents)


class Resource(models.Model):
    """
    User's resource assignment, using get_FOO_display to get display name like Server
    """
    RESOURCE_TYPES = (
        (SERVER, 'Server'),
        (VOLUME, 'Volume'),
        (STORAGE, 'Storage'),
        (HOST, 'Host'),
        (NETWORK, 'Network'),
    )

    id = models.CharField(primary_key=True, max_length=36)
    type = models.CharField(max_length=255, choices=RESOURCE_TYPES,
                            verbose_name=_('type'))
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    task_id = models.CharField(max_length=255, null=True)  # This field stores celery task id

    class Meta:
        ordering = ['type']
        db_table = 'resource'
        default_permissions = ()
