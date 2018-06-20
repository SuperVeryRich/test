# coding=utf-8
"""
Rebuild database
"""
from MySQLdb import connect
from ecloud.settings import DATABASES
from .clean_migration_files import main as clean_migrations

DEFAULT_DB = DATABASES['default']


class RebuildDatabase:

    def __init__(self):
        self.conn = self._get_conn()

    @staticmethod
    def _get_conn():
        return connect(host=DEFAULT_DB['HOST'],
                       user=DEFAULT_DB['USER'],
                       password=DEFAULT_DB['PASSWORD'],
                       db=DEFAULT_DB['NAME'],
                       port=DEFAULT_DB['PORT'])

    def drop_db(self):
        cur = self.conn.cursor()
        cur.execute('DROP DATABASE IF EXISTS %s' % DEFAULT_DB['NAME'])
        cur.close()

    def rebuild_db(self):
        cur = self.conn.cursor()
        cur.execute('CREATE DATABASE IF NOT EXISTS %s '
                    'DEFAULT CHARSET utf8 COLLATE utf8_general_ci;' % DEFAULT_DB['NAME'])
        cur.close()

    def _close_conn(self):
        try:
            self.conn.close()
        except Exception as e:
            print(str(e))
            pass


def main():
    clean_migrations()

    print('Database %s be permanently deleted!' % DEFAULT_DB['name'])
    user_input = input('Are you sure? (y/n): ')
    if user_input in ('y', 'yes'):
        obj = RebuildDatabase()
        obj.drop_db()
        obj.rebuild_db()
    else:
        print('Canceled')


if __name__ == '__main__':
    main()

