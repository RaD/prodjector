# -*- coding: utf-8 -*-

from fabric.api import env, settings, cd, run
from fabric.contrib import files
from fab_deploy import utils

from .supervisord import supervisorctl

TYPE = 'COMPONENT'
NAME = 'RubyRep'
APT = ['rubygems',]
PIP = []

def deploy():
    u"""
    Установка RubyRep...
    """
    print deploy.__doc__

    @utils.run_as_sudo
    def install():
        run('gem install postgres  --no-rdoc --no-ri --install-dir %s' % env.conf.ENV_DIR)
        run('gem install rubyrep  --no-rdoc --no-ri --install-dir %s' % env.conf.ENV_DIR)

    install()


def setup():
    u"""
    Настройка RubyRep...
    """
    print setup.__doc__
    base_dir = '%s/%s' % (env.conf.ENV_DIR, 'etc')
    run('mkdir -p %s/supervisord' % base_dir)
    files.upload_template('./tpls/supervisor_rubyrep.template',
                          '%s/%s' % (base_dir, 'supervisord/rubyrep.ini'),
                          env.conf, use_jinja=True)



def final():
    u"""
    Запуск RubyRep...
    """
    print u'Supervisor is responsible for RubyRep now.'

