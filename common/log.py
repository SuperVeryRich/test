import logging


__all__ = [
    'Logging',
]


class LoggingBase(object):

    @property
    def default_logger(self):
        return logging.getLogger('default')

    @property
    def script_logger(self):
        return logging.getLogger('script')

    @property
    def task_logger(self):
        return logging.getLogger('task')

    @staticmethod
    def custom_logger(logger_name):
        """
        Should be added in settings.py
        :return:
        """
        return logging.getLogger(logger_name)


Logging = LoggingBase()
