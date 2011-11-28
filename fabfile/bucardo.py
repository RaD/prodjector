# -*- coding: utf-8 -*-

from fabric.api import env, settings, cd, run
from fabric.contrib import files
from fab_deploy import utils

from .supervisord import supervisorctl

TYPE = 'COMPONENT'
NAME = 'Bucardo'
APT = ['libnet-daemon-perl', 'libdbi-perl', 'libdbd-pg-perl',
       'libplrpc-perl', 'libdbix-safe-perl', 'unzip',
       'postgresql-plperl-8.4',]
PIP = []

def deploy():
    u"""
    Установка Bucardo...
    """
    print deploy.__doc__

    @utils.run_as_sudo
    def install():
        run('make install')

    with cd('/tmp'):
        run('wget -c -O bucardo-4.4.3.zip https://github.com/bucardo/bucardo/zipball/4.4.3')
        run('unzip bucardo-4.4.3.zip')
        return
        with cd('bucardo-bucardo-2481d74'):
            run('perl Makefile.PL')
            run('make')
            install()


def setup():
    u"""
    Настройка Bucardo...
    """
    print setup.__doc__
    base_dir = '%s/%s' % (env.conf.ENV_DIR, 'etc')
    run('mkdir -p %s/supervisord' % base_dir)
    files.upload_template('./tpls/supervisor_bucardo.template',
                          '%s/%s' % (base_dir, 'supervisord/bucardo.ini'),
                          env.conf, use_jinja=True)


    print u"""
Add databases:

  bucardo_ctl add database <dbname>

Add tables and sequences:

  bucardo_ctl add all tables
  bucardo_ctl add all sequences

Add syncs:

  bucardo_ctl add sync <syncname> type=<synctype> source=<db> targetdb=<db> tables=tab1,tab2,...

Start Bucardo:

  bucardo_ctl start
    """

def final():
    u"""
    Запуск Bucardo...
    """
    print u'Supervisor is responsible for Redis now.'

