# coding=utf-8
from .base import OpenStackRequest
from ..models import get_project_model
from ..utils.request_ import validate_param

Project = get_project_model()


class KeystoneRequest(OpenStackRequest):

    ks_version = 'v3'

    def __init__(self):
        super().__init__('keystone')

    def list_project(self, request, name=None, enabled=True):
        """
        List projects
        /v3/projects
        """
        path = '/v3/projects'
        result = self.get(request, path,
                          params={'name': name, 'enabled': enabled})
        return result

    def get_project(self, request, project_id, **kwargs):
        """
        Show project details
        /v3/projects/{project_id}
        """
        path = '/v3/projects/%s' % project_id
        return self.get(request, path, **kwargs)

    def create_project(self, request, name, is_domain=False, description=None,
                       enabled=True, **kwargs):
        """
        Creates a project, where the project may act as a domain.
        /v3/projects
        """
        path = '/v3/projects'
        data = {
            "project": {
                "description": description,
                "enabled": enabled,
                "is_domain": is_domain,
                "name": name
            }
        }
        result = self.post(request, path, data=data, **kwargs)

        # create a project model object
        project_id = result['project']['id']
        Project.objects.create(id=project_id, user__id=request.user.id)

        return result

    def update_project(self, request, project_id, name=None, is_domain=None,
                       description=None, enabled=None, **kwargs):
        """
        Update project
        /v3/projects/{project_id}
        """
        path = '/v3/projects/%s' % project_id
        data = {
            "project": {}
        }
        if name is not None:
            data['project']['name'] = name
            validate_param(name, str)
        if is_domain is not None:
            validate_param(is_domain, bool)
            data['project']['is_domain'] = is_domain
        if description is not None:
            validate_param(description, str)
            data['project']['description'] = description
        if enabled is not None:
            validate_param(enabled, bool)
            data['project']['enabled'] = enabled

        return self.patch(request, path, data=data, **kwargs)

    def delete_project(self, request, project_id, **kwargs):
        """
        Delete a project
        /v3/projects/{project_id}
        """
        path = '/v3/projects/%s' % project_id
        return self.delete(request, path, **kwargs)

    def list_regions(self, request, **kwargs):
        """
        List regions
        /v3/regions
        """
        path = '/v3/regions'
        return self.get(request, path, **kwargs)
