# coding=utf-8

KEYSTONE = {
    'host': '10.10.132.161',
    'port': 5000,
    'user': 'admin',
    'pass': '06a29a1b7d84cb7b713a',
    'token_timeout': 12 * 60 * 60,  # keystone token timeout, seconds
    'project_id': 'c5bb6219baf84706aba37bf9f37ea911',   # should active
}

MOCK_TOKEN = 'a19bc13b46ba459cb3104fa97e414a27'

OPENSTACK = {
    'keystone': KEYSTONE
}
