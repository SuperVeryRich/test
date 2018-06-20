from django.apps import apps as django_apps

__all__ = [
    'Storage',
    'Instances',
    'Volumes',
    'ComputeNodes',
    'get_resource_model',
    'get_project_model'
]


def get_storage_model():
    return django_apps.get_model('storage.Storage', require_ready=False)


def get_nova_instance_model():
    return django_apps.get_model('compute.Instances', require_ready=False)


def get_cinder_volume_model():
    return django_apps.get_model('storage.Volumes', require_ready=False)


def get_nova_compute_nodes_model():
    return django_apps.get_model('compute.ComputeNodes', require_ready=False)


def get_resource_model():
    return django_apps.get_model('identity.Resource', require_ready=False)


def get_project_model():
    return django_apps.get_model('identity.Project', require_ready=False)


Storage = get_storage_model()
Instances = get_nova_instance_model()
Volumes = get_cinder_volume_model()
ComputeNodes = get_nova_compute_nodes_model()
