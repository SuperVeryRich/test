from .base import OpenStackRequest
from ..utils.request_ import validate_param


class CinderRequest(OpenStackRequest):

    def __init__(self):
        super().__init__('cinder')

    def get_volume_type(self, request, type_id, **kwargs):
        """
        Get details for a volume type
        /v3/{project_id}/types/{volume_type_id}
        """
        path = '/v3/%s/types/%s' % (request.user.project_id, type_id)
        return self.get(request, path, *kwargs)

    def list_volume_types(self, request, sort=None, limit=None,
                          offset=None, marker=None, **kwargs):
        """
        List all volume types
        /v3/{project_id}/types
        """
        path = '/v3/%s/types' % request.user.project_id
        query = {'sort': sort, 'limit': limit, 'offset': offset,
                 'marker': marker}
        return self.get(request, path, query=query, **kwargs)

    def create_volume_type(self, request, type_name, **kwargs):
        """
        Create a volume type
        /v3/{project_id}/types
        """
        # TODO: ensure that user must be in a project
        path = '/v3/%s/types' % request.user.project_id
        data = {
            "volume_type": {
                "name": type_name,
                "description": kwargs.get('description'),
                "os-volume-type-access:is_public":
                    kwargs.get('os-volume-type-access:is_public', True),
                "extra_specs": kwargs.get('extra_specs', {})
            }
        }
        return self.post(request, path, data=data, **kwargs)

    def delete_volume_type(self, request, volume_type_id, **kwargs):
        """
        Delete a volume type
        /v3/{project_id}/types/{volume_type_id}
        """
        path = '/v3/%s/types/%s' % (request.user.project_id, volume_type_id)
        return self.delete(request, path, **kwargs)

    def get_volume(self, request, volume_id):
        """
        Show a volume’s details
        /v3/{project_id}/volumes/{volume_id}
        """
        path = '/v3/%s/volumes/%s' % (request.user.project_id, volume_id)
        return self.get(request, path)

    def list_volumes(self, request, project_id, detail=False, **kwargs):
        """
        List accessible volumes (combine two API into one)
        /v3/{project_id}/volumes
        /v3/{project_id}/volumes/detail
        """
        path = '/v3/%s/volumes' % project_id
        if detail:
            path += '/detail'
        return self.get(request, path, **kwargs)

    def create_volume(self, request, name, size,
                      availability_zone=None,
                      source_volid=None,
                      description=None,
                      multiattach=False,
                      snapshot_id=None,
                      backup_id=None,
                      image_ref=None,
                      volume_type=None,
                      metadata=None,
                      consistencygroup_id=None,
                      scheduler_hints=None,
                      **kwargs):
        """
        Create a volume
        /v3/{project_id}/volumes
        """
        path = '/v3/%s/volumes' % request.user.project_id
        data = {
            "volume": {
                "size": size,
                "availability_zone": availability_zone,
                "source_volid": source_volid,
                "description": description,
                "multiattach": multiattach,
                "snapshot_id": snapshot_id,
                "backup_id": backup_id,
                "name": name,
                "imageRef": image_ref,
                "volume_type": volume_type,
                "metadata": metadata,
                "consistencygroup_id": consistencygroup_id
            }
        }
        if kwargs.get('scheduler_hints'):
            data['OS-SCH-HNT:scheduler_hints'] = scheduler_hints
        return self.post(request, path, data=data, **kwargs)

    def update_volume(self, request, volume_id, description=None,
                      name=None, metadata=None, **kwargs):
        """
        Update a volume, can update name, description and metadata
        /v3/{project_id}/volumes/{volume_id}
        """
        path = '/v3/%s/volumes/%s' % (request.user.project_id, volume_id)
        volume = {}
        if description:
            volume['description'] = description
        if name:
            volume['name'] = name
        if metadata:
            volume['metadata'] = metadata
        data = {"volume": volume}
        return self.put(request, path, data=data, **kwargs)

    def delete_volume(self, request, volume_id, **kwargs):
        """
        Delete a volume
        /v3/{project_id}/volumes/{volume_id}

        Preconditions:
            Volume status must be available, in-use, error, or error_restoring.
            You cannot already have a snapshot of the volume.
            You cannot delete a volume that is in a migration.
        """
        path = '/v3/%s/volumes/%s' % (request.user.project_id, volume_id)
        return self.delete(request, path, **kwargs)

    def get_volume_metadata_by_key(self, request, volume_id, key, **kwargs):
        """
        Show a volume’s metadata for a specific key
        /v3/{project_id}/volumes/{volume_id}/metadata/{key}

        Response example:
            {
              "meta": {
                "name": "test"
              }
            }
        """
        path = '/v3/%s/volumes/%s/metadata/%s' % (request.user.project_id,
                                                  volume_id, key)
        return self.get(request, path, **kwargs)

    def update_volume_metadata_by_keys(self, request, volume_id, key_values,
                                       **kwargs):
        """
        Update a volume’s metadata
        /v3/{project_id}/volumes/{volume_id}/metadata

        Request example:
        {
            "metadata": {
                "name": "metadata1",
                "status": "metadata2"
            }
        }
        key_values: [('name', 'metadata1'), ('status', 'metadata2') ...]
        """
        assert key_values and isinstance(key_values, (list, tuple))
        for item in key_values:
            # keys and values must be string
            validate_param(item, str)
        path = '/v3/%s/volumes/%s/metadata' % (request.user.project_id, volume_id)
        data = {'metadata': {}}
        for k, v in key_values:
            data['metadata'][k] = v

        return self.put(request, path, data=data, **kwargs)

    def update_volume_metadata_by_key(self, request, volume_id, key, value,
                                      **kwargs):
        """
        Update a volume’s metadata for a specific key
        /v3/{project_id}/volumes/{volume_id}/metadata/{key}
        """
        validate_param((key, value), str)
        path = '/v3/%s/volumes/%s/metadata/%s' % (request.user.project_id,
                                                  volume_id, key)
        data = {
            "meta": {
                key: value
            }
        }
        return self.put(request, path, data=data, **kwargs)

    def delete_volume_metadata_by_key(self, request, volume_id, key, **kwargs):
        """
        Delete a volume’s metadata
        /v3/{project_id}/volumes/{volume_id}/metadata/{key}
        """
        path = '/v3/%s/volumes/%s/metadata/%s' % (request.user.project_id,
                                                  volume_id, key)
        return self.delete(request, path, **kwargs)

    def extend_volume_size(self, request, volume_id, new_size, **kwargs):
        """
        Extend a volume size (GB)
        :return:
        """
        assert isinstance(new_size, int)
        path = '/v3/%s/volumes/%s/action' % (request.user.project_id, volume_id)
        data = {
            "os-extend": {
                "new_size": new_size
            }
        }
        return self.post(request, path, data=data, **kwargs)

    def revert_volume_to_latest_snapshot(self, request, volume_id, snapshot_id,
                                         **kwargs):
        """
        Revert a volume to its latest snapshot, this API only support reverting
        a detached volume, and the volume status must be available.
        Available since API microversion 3.40.
        """
        validate_param(snapshot_id, 'uuid')
        path = '/v3/%s/volumes/%s/action' % (request.user.project_id, volume_id)
        data = {
            "revert": {
                "snapshot_id": snapshot_id
            }
        }
        return self.post(request, path, data=data, **kwargs)

    def attach_volume_to_server(self, request, volume_id, instance_id,
                                mountpoint, **kwargs):
        """
        Attach volume to a server

        Preconditions:
            Volume status must be available.
            You should set instance_uuid or host_name.
        """
        validate_param((volume_id, instance_id), 'uuid')
        path = '/v3/%s/volumes/%s/action' % (request.user.project_id, volume_id)
        data = {
            "os-attach": {
                "instance_uuid": instance_id,
                "mountpoint": mountpoint
            }
        }
        return self.post(request, path, data=data, **kwargs)

    def detach_volume_from_server(self, request, volume_id, **kwargs):
        """
        Detach volume from server
        Preconditions:
            Volume status must be in-use.
        """
        validate_param(volume_id, 'uuid')
        path = '/v3/%s/volumes/%s/action' % (request.user.project_id, volume_id)
        data = {
            "os-detach": {
                "attachment_id": volume_id
            }
        }
        return self.post(request, path, data=data, **kwargs)

    def force_delete_volume(self, request, volume_id, **kwargs):
        """
        Attempts force-delete of volume, regardless of state.
        """
        path = '/v3/%s/volumes/%s/action' % (request.user.project_id, volume_id)
        data = {
            "os-force_delete": {}
        }
        return self.post(request, path, data=data, **kwargs)
