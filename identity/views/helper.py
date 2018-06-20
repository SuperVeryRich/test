from common.constants.resources import *
from common.models import Instances, Volumes, ComputeNodes, get_resource_model
from identity.models import Permission

Resource = get_resource_model()


def get_permissions():
    return Permission.objects.exclude(
        content_type__app_label__in=['contenttypes', 'sessions'])


# def _get_resource_detail(resource_obj):
#     name = None
#     if resource_obj.type == VOLUME:
#         obj = Volumes.objects.get(id=resource_obj.id)
#     elif resource_obj.type == HOST:
#         obj = ComputeNodes.objects.get(id=resource_obj.id)
#     elif resource_obj.type == SERVER:
#         obj = Instances.objects.get(uuid=resource_obj.id)
#     elif resource_obj.type == STORAGE:
#         obj = None
#         name = None
#     elif resource_obj.type == NETWORK:
#         obj = None
#         name = None
#     else:
#         raise ValueError
#     if name is None:
#         if resource_obj.type == HOST:
#             name = obj.host
#         else:
#             name = obj.display_name
#     resource_obj.display_name = name
#     return resource_obj
#
#
# def resource_detail(id_or_obj):
#     """
#     resource detail from nova, cinder ...
#     :param id_or_obj:
#     :return:
#     """
#     if isinstance(id_or_obj, str):
#         resource_obj = Resource.objects.get(id=id_or_obj)
#         resource_obj = _get_resource_detail(resource_obj)
#
#     elif isinstance(id_or_obj, Resource):
#         resource_obj = _get_resource_detail(id_or_obj)
#     else:
#         raise ValueError
#     return resource_obj

