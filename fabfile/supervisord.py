# -*- coding: utf-8 -*-

from fabric.api import env, settings, cd, run
from fabric.contrib import files
from fab_deploy import crontab, utils

TYPE = 'SERVICE'
NAME = 'Supervisor'
APT = []
PIP = ['supervisor',]

def setup():
    u"""
    Настройка Supervisor.
    """
    print setup.__doc__
    with cd(env.conf.ENV_DIR):
        run('mkdir -p var/{log,run} etc/supervisord')
    base_dir = '%s/%s' % (env.conf.ENV_DIR, 'etc')
    run('mkdir -p %s' % base_dir)
    files.upload_template('./tpls/supervisord.template',
                          '%s/%s' % (base_dir, 'supervisord.conf'),
                          env.conf, use_jinja=True)

    supervisord_bin = env.conf.ENV_DIR + '/bin/supervisord'
    crontab.crontab_update('@reboot ' + supervisord_bin, 'supervisord-boot')

def final():
    u"""
    Запуск Supervisor...
    """
    supervisord_reload()

def _pid():
    pid_file = '%s/var/run/supervisord-%s.pid' % (env.conf.ENV_DIR, env.conf.INSTANCE_NAME)
    pid = run('cat '+pid_file)
    return pid

@utils.inside_virtualenv
def supervisord_reload():
    """ Reloads supervisord """

    pid = _pid()
    if pid.succeeded:
        run('kill -1 %s' % pid)
    else:
        with settings(warn_only=True):
            res = run('supervisord')
            if res.succeeded: # new supervisord was started
                pid = _pid()

        # and restarts it (recreating pid file if necessary)
        run('kill -1 %s' % pid)


def supervisord_update(program):
    """ Updates supervisord config for a given program """
    name = program+".ini"
    utils.upload_config_template(
        'supervisord/' + name,
        env.conf['ENV_DIR']+'/etc/supervisord/'+name
    )
    supervisord_reload()

def supervisord_remove(program):
    """ Removes supervisord config for a given program """
    filename = env.conf['ENV_DIR']+'/etc/supervisord/'+program+'.ini'
    run('rm '+ filename)
    supervisord_reload()

def supervisord_show_log():
    """ Shows supervisord log """
    log = env.conf['PROJECT_DIR']+'/files/logs/supervisord.log'
    run('cat ' + log)

@utils.inside_virtualenv
def supervisorctl(commands):
    config_path = '%s/%s/%s' % (env.conf.ENV_DIR, 'etc', 'supervisord.conf')
    if files.exists(config_path):
        run('supervisorctl %s' % (commands))
