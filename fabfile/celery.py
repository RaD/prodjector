# -*- coding: utf-8 -*-
from fabric.api import env, run
from fabric.contrib import files
from fab_deploy import utils

from .supervisord import supervisorctl

TYPE = 'COMPONENT'
NAME = 'Celery'
APT = []
PIP = ['celery==2.3.3', 'django-celery==2.3.3',]

def deploy():
    u"""
    Установка Celery...
    """
    print u'Celery is installed on PIP level.'

def setup():
    u"""
    Настройка Celery...
    """
    print setup.__doc__
    base_dir = '%s/%s' % (env.conf.ENV_DIR, 'etc')
    run('mkdir -p %s/supervisord' % base_dir)
    files.upload_template('./tpls/supervisor_celery.template',
                          '%s/%s' % (base_dir, 'supervisord/celery.ini'),
                          env.conf, use_jinja=True)

def final():
    u"""
    Запуск Celery...
    """
    print u'Supervisor is responsible for Celery now.'


@utils.inside_virtualenv
def celery_restart():
    supervisorctl('stop celery-io celery-processes celerybeat')
    supervisorctl('stop celerycam')
    celery_drop_events()
    supervisorctl('start celerycam celery-io celery-processes celerybeat')

@utils.inside_virtualenv
def celery_drop_events():
    # грязный хак, см.
    # https://github.com/ask/celery/issues/436
    # https://bitbucket.org/kmike/zina/issue/105/redis

    # считаем, что все очереди на этом этапе - это баги
    stall_queues = run('redis-cli keys "celeryev.*"').splitlines()
    stall_queues = [q.split('"')[1] for q in stall_queues if '"' in q]
    run('redis-cli del ' + ' '.join(stall_queues))
    run('redis-cli del _kombu.binding.celeryev')
