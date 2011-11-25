# -*- coding: utf-8 -*-

CONFIG = {
    'DEBUG': True,
    'SECRET_KEY': '123abc456',
    'SSH_PUBLIC_KEY_PATH': '/home/rad/.ssh/ruslan.popov.pub',
    'VIRTUALBOX': 'zina@localhost:9022',
    'CACHE_PATH_LOCAL': './caches',
    'CACHE_PATH_REMOTE': '/tmp',
    'ADMINS': (
        ('Ruslan Popov', '<ruslan@zina.ru>'),
        ),
    'DATABASES': {
        'default': {
            'ENGINE': 'django.contrib.gis.db.backends.postgis',
            'NAME': 'zina',
            'USER': 'zina',
            'PASSWORD': 'q1',
            },
        },
    'STATIC_ROOT': 'static',
    'PRODJECTOR': {
        'COMPONENTS': (
            'postgres',
            'supervisord',
            'redis',
            'celery',
            ),
        },
    }

