# coding=utf-8
"""
通过提交的POST数据与标准数据对比，来校验Post参数的合法性

"""
import re
from django.urls import converters
from common.exceptions import InvalidParameters
from common.openstack.constants import KEYSTONE


def validate_param(value, p_type, length=None, max_length=None, min_length=None):
    """

    """
    # TODO: This can be optimized by Open-source libraries
    if not isinstance(value, (list, tuple)):
        value = [value]
    for item in value:
        p_type = p_type.lower()
        if p_type == 'uuid':
            if not re.match(converters.UUIDConverter.regex, item):
                raise InvalidParameters
        elif p_type == 'int' or p_type is int:
            if not re.match(converters.IntConverter.regex, str(item)):
                raise InvalidParameters
        elif p_type == 'str' or p_type is str:
            if not all((re.match(converters.StringConverter.regex, item),
                        isinstance(item, str))):
                raise InvalidParameters
        elif p_type == 'bool' or p_type is bool:
            if not isinstance(value, bool):
                raise InvalidParameters
        else:
            raise ValueError('Not supported value type: %s' % str(type(item)))
        if length and len(item) != length:
            raise InvalidParameters
        if max_length and len(item) > max_length:
            raise InvalidParameters
        if min_length and len(item) < min_length:
            raise InvalidParameters


def request_serializer(request):
    """
    Serialize request object to jsonable object,
    used for celery task
    """
    print('serializer')
    return {
        'user': {
            'id': request.user.id,
            'project_id': KEYSTONE['project_id']
        },
        'session': {
            'token': request.session.get('token')
        },
        'POST': request.POST,
        'GET': request.GET
    }