# coding=utf-8
import requests
import json
from common.exceptions import ImproperConfiguration
from common.log import Logging
from .constants import OPENSTACK
import time
# from urllib.parse import urlunparse


Log = Logging.default_logger


SERVICE_TYPES = {
    'nova': 8774,
    'cinder': 8776,
    'keystone': 5000,
    'neutron': 9696
}


class OpenStackRequest(object):

    connect_timeout, read_timeout = 5.0, 30.0
    timeout = (connect_timeout, read_timeout)

    def __init__(self, service_type):
        """
        :param service_type: OpenStack service types
        """
        assert service_type.lower() in [_ for _ in SERVICE_TYPES]
        self.service_type = service_type

        try:
            ks = OPENSTACK['keystone']
            self.ks_user = ks['user']
            self.ks_pass = ks['pass']
            self.ks_host = ks['host']
            self.ks_port = ks['port']
            self.ks_timeout = ks['token_timeout']
            self.ks_project_id = ks['project_id']
            assert all((self.ks_user, self.ks_pass, self.ks_host,
                        self.ks_port, self.ks_timeout))
            assert isinstance(self.ks_port, int)
            assert isinstance(self.ks_timeout, int)
        except (KeyError, AssertionError) as e:
            raise ImproperConfiguration(str(e))

    # @staticmethod
    # def _get_query_string(query_dict):
    #     """
    #     Transfer query dict to query string
    #     {'name': 'test', 'enable': True} => ?name=test&enable=true
    #     """
    #     assert isinstance(query_dict, dict)
    #     result = str()
    #     for k, v in query_dict.items():
    #         if v is not None:
    #             if isinstance(v, bool):
    #                 v = str(v).lower()
    #             result += '%s=%s&' % (k, v)
    #     if result:
    #         result.rstrip('&')
    #     return result

    def _get_token(self):
        # TODO: request token from OpenStack
        data = {
            "auth": {
                "identity": {
                    "methods": [
                        "password"
                    ],
                    "password": {
                        "user": {
                            "name": self.ks_user,
                            "domain": {
                                "name": 'default'
                            },
                            "password": self.ks_pass
                        }
                    }
                }
            }
        }
        try:
            res = requests.post('http://%s:%d/v3/auth/token'
                                % (self.ks_host, self.ks_port),
                                data=data,
                                timeout=self.timeout,
                                headers=self._get_header(None))
        except Exception as e:
            Log.debug('Request token from keystone error: %s' % str(e))
            raise e
        headers = res.headers
        return json.loads(headers['x-subject-token'])

    def get_token(self, request):
        """
        Get token from django request or get token from OpenStack

        When a user send a request to OpenStack first time, a token request
        will be sent and store token in user's session.
        Later we use this token to send request.

        """
        # {'id': '', 'created_at': ''}
        if isinstance(request, dict):
            # serialized request
            token = request['session'].get('token')
        else:
            token = request.session.get('token')
        if token:
            created_at = token['created_at']
            if time.time() - created_at >= self.ks_timeout:
                return self._get_token()
            return token['id']
        else:
            return self._get_token()

    def _get_header(self, request):
        if request is not None:
            return {'Content-Type': 'application/json',
                    'X-Auth-Token': self.get_token(request)}
        else:
            # request token
            return {'Content-Type': 'application/json'}

    def _full_url(self, path):
        """Build full URL"""
        if not path.startswith('/'):
            raise ValueError('URL should start with "/", '
                             'e.g. /v3/{project_id}/volumes')
        path = path.rstrip('/')
        # scheme = 'http'
        # netloc = '%s:%d' % (self.ks_host, SERVICE_TYPES[self.service_type])
        # query = self._get_query_string(query) if query else None
        # return urlunparse([scheme, netloc, path, params, query, fragment])
        return 'http://%s:%d' % (self.ks_host,
                                 SERVICE_TYPES[self.service_type]) + path

    def get(self, request, path, params=None, **kwargs):
        """
        OpenStack get interface
        :param request: request /serialized object
        :param path: e.g. /v3/project
        :param params: e.g. {'name': 'test', 'enabled': True}
        :param kwargs:
        :return:
        """
        # Think about if token is not active
        payload = requests.get(self._full_url(path),
                               params=params,
                               timeout=self.timeout,
                               headers=self._get_header(request), **kwargs)
        return payload

    def post(self, request, path, data=None, json_data=None, **kwargs):
        payload = requests.post(self._full_url(path), data=data, json=json_data,
                                timeout=self.timeout,
                                headers=self._get_header(request), **kwargs)
        return payload

    def put(self, request, path, data=None, **kwargs):
        payload = requests.put(self._full_url(path), data=data,
                               timeout=self.timeout,
                               headers=self._get_header(request), **kwargs)
        return payload

    def delete(self, request, path, **kwargs):
        payload = requests.delete(self._full_url(path),
                                  timeout=self.timeout,
                                  headers=self._get_header(request), **kwargs)
        return payload

    def patch(self, request, path, data=None, **kwargs):
        payload = requests.patch(self._full_url(path), data=data,
                                 timeout=self.timeout,
                                 headers=self._get_header(request), **kwargs)
        return payload
