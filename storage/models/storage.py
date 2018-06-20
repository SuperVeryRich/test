from django.db import models
from django.utils.translation import ugettext_lazy as _


class Storage(models.Model):
    """
    Storage modal
    """
    id = models.CharField(primary_key=True, max_length=36)
    name = models.CharField(max_length=255, verbose_name=_('name'))
    # storage type classified by protocols, e.g. iSCSI, NFS, Ceph ...
    type = models.CharField(max_length=20, verbose_name=_('storage type'))
    # backend name is a volume backend name in cinder
    backend_name = models.CharField(max_length=255, verbose_name=_('volume type'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('created at'))

    class Meta:
        db_table = 'storage'
        permissions = (
            ('list_storage', _('Can see storage list')),
            ('detail_storage', _('Can see storage detail')),
            ('create_storage', _('Can create storage')),
            ('update_storage', _('Can update storage')),
            ('delete_storage', _('Can delete storage')),
        )
        default_permissions = ()
