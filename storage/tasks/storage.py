import time
from celery import shared_task, chain
from celery.task import Task
from common.models import get_resource_model
from common.openstack.cinder import CinderRequest

Resource = get_resource_model()
R = CinderRequest()


class StorageCreateTask(Task):

    def run(self, *args, **kwargs):
        pass

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        print('{0!r} failed: {1!r}'.format(task_id, exc))

    def on_success(self, retval, task_id, args, kwargs):
        print('{0!r} success: {1!r}'.format(task_id, retval))


@shared_task(base=StorageCreateTask, bind=True)
def _create_volume_type(self, request, data, *args, **kwargs):
    """

    :param request:
    :param project_id:
    :param args:
    :param kwargs:
    :return:
    """
    print('_create_volume_type start')
    # check image
    # check storage state and free space

    print('task_id: %s' % self.request.id)
    time.sleep(5)
    result = R.create_volume_type(request, data)
    # result = {
    #     "volume_type": {
    #         "name": "test_type",
    #         "extra_specs": {},
    #         "os-volume-type-access:is_public": True,
    #         "is_public": True,
    #         "id": "6d0ff92a-0007-4780-9ece-acfe5876966a",
    #         "description": "test_type_desc"
    #     }
    # }
    print('_create_volume_type end')
    return result


@shared_task(base=StorageCreateTask, bind=True)
def create_storage(request, **kwargs):
    time.sleep(10)


if __name__ == '__main__':
    pass