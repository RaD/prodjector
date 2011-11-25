# -*- coding: utf-8 -*-

from fabric.api import env, settings, cd, run
from fabric.contrib import files

from .supervisord import supervisorctl

TYPE = 'DATABASE'
NAME = 'Redis'
APT = []
PIP = ['redis==2.4.10',]

def deploy():
    u"""
    Установка Redis...
    """
    print deploy.__doc__

    with settings(warn_only=True):
        supervisorctl('stop redis')

    with cd('/tmp'):
        file_name = 'redis-2.4.1.tar.gz'
        run('wget -c http://redis.googlecode.com/files/%s' % file_name)
        run('tar -xzf %s' % file_name)
        with cd('redis-2.4.1'):
            run('make')
            run('make PREFIX=%s install' % env.conf.ENV_DIR)

def setup():
    u"""
    Настройка Redis...
    """
    print setup.__doc__
    base_dir = '%s/%s' % (env.conf.ENV_DIR, 'etc')
    run('mkdir -p %s/supervisord' % base_dir)
    files.upload_template('./tpls/redis.template',
                          '%s/%s' % (base_dir, 'redis.conf'),
                          env.conf, use_jinja=True)
    files.upload_template('./tpls/supervisor_redis.template',
                          '%s/%s' % (base_dir, 'supervisord/redis.ini'),
                          env.conf, use_jinja=True)

def final():
    u"""
    Запуск Redis...
    """
    print u'Supervisor is responsible for Redis now.'

