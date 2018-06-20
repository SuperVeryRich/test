from celery.worker.request import Request
from common.log import Logging


LOG = Logging.task_logger


class MyRequest(Request):
    """A minimal custom request to log failures and hard time limits."""

    def on_timeout(self, soft, timeout):
        super(MyRequest, self).on_timeout(soft, timeout)
        if not soft:
            LOG.warning(
                'A hard timeout was enforced for task %s',
                self.task.name
            )

    def on_failure(self, exc_info, send_failed_event=True, return_ok=False):
        super().on_failure(
            exc_info,
            send_failed_event=send_failed_event,
            return_ok=return_ok
        )
        LOG.warning(
            'Failure detected for task %s',
            self.task.name
        )
