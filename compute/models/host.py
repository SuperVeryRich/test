# coding=utf-8
from django.db import models
from django.utils.translation import ugettext_lazy as _


class Host(models.Model):
    """
    宿主机
    """
    id = models.SmallIntegerField(primary_key=True)
    hostname = models.CharField(max_length=255, verbose_name=_('hostname'))
    ipv4 = models.GenericIPAddressField(verbose_name=_('IPv4 address'))
    description = models.CharField(max_length=255, verbose_name=_('description'))

    class Meta:
        # db_table = 'host'
        permissions = (
            ('list_host', _('Can see host list')),
            ('detail_host', _('Can see host detail')),
            ('create_host', _('Can create host')),
            ('update_host', _('Can update host')),
            ('delete_host', _('Can delete host')),
        )
        default_permissions = ()
