# Create your tasks here
import time
from common.log import Logging
from celery import shared_task, chain
from celery.task import Task
from common.openstack.cinder import CinderRequest
from common.exceptions import InvalidParameters
from common.models import Volumes, get_resource_model
from common.utils.text_ import UUID

Resource = get_resource_model()

LOG = Logging.task_logger

R = CinderRequest()


class VolumeCreateTask(Task):

    def run(self, *args, **kwargs):
        pass

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        print('{0!r} failed: {1!r}'.format(task_id, exc))

    def on_success(self, retval, task_id, args, kwargs):
        print('{0!r} success: {1!r}'.format(task_id, retval))


@shared_task(base=VolumeCreateTask, bind=True)
def create_volume(self, request):
    print(self)
    data = request['POST']
    print(data)
    name, size = data.get('name'), data.get('size')
    if not all((name, size, str(size).isdigit())):
        raise InvalidParameters

    print('_create_volume start')
    # result = R.create_volume(request, name, size)
    # mock start
    time.sleep(15)
    random_uuid = UUID.uuid4
    result = {
        "volume": {
            "status": "creating",
            "migration_status": None,
            "user_id": "0eea4eabcf184061a3b6db1e0daaf010",
            "attachments": [],
            "links": [
                {
                    "href": "http://23.253.248.171:8776/v3/bab7d5c60cd041a0a36f7c4b6e1dd978/volumes/6edbc2f4-1507-44f8-ac0d-eed1d2608d38",
                    "rel": "self"
                },
                {
                    "href": "http://23.253.248.171:8776/bab7d5c60cd041a0a36f7c4b6e1dd978/volumes/6edbc2f4-1507-44f8-ac0d-eed1d2608d38",
                    "rel": "bookmark"
                }
            ],
            "availability_zone": "nova",
            "bootable": "false",
            "encrypted": False,
            "created_at": "2015-11-29T03:01:44.000000",
            "description": None,
            "updated_at": None,
            "volume_type": "lvmdriver-1",
            "name": "test-volume-attachments",
            "replication_status": "disabled",
            "consistencygroup_id": None,
            "source_volid": None,
            "snapshot_id": None,
            "multiattach": False,
            "metadata": {},
            "id": random_uuid,
            "size": size
        }
    }
    Volumes.objects.create(id=random_uuid,
                           size=2,)
    # mock end

    print('_create_volume end')
    # TODO: assign user's object permission after volume creating finished
    user_obj = None
    volume_obj = None

    # update resource
    print('task_id: %s' % self.request.id)
    resource = Resource.objects.filter(task_id=self.request.id)
    if not resource.exists():
        raise ValueError    # TODO: replace this exception

    # update it regardless of status
    resource.update(id=result['volume']['id'], task_id=None)
    # and more if it is needed

