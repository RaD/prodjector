# -*- coding: utf-8 -*-

import os
from fabric.api import env, run, local, put
from fabric.contrib.files import append as append_line
from fab_deploy import utils
from .configuration import CONFIG

def setup_key_auth(no_password=True):
    u"""
    Настройка авторизации по ключам.
    """
    public_key_path = CONFIG.get('SSH_PUBLIC_KEY_PATH')
    if not public_key_path:
        raise RuntimeError(u'Check SSH_PUBLIC_KEY_PATH parameter!')

    try:
        with open(public_key_path, 'r') as key:
            print 'Installing public key:'
            print key.read()
            key.close()
    except IOError:
        raise RuntimeError(u"File %s doesn't exist!" % public_key_path)

    print setup_key_auth.__doc__
    run('mkdir -p ~/.ssh')
    run('chmod 700 ~/.ssh')
    put(public_key_path, '~/.ssh/new_key', mode=0600)
    run('cat ~/.ssh/new_key >> ~/.ssh/authorized_keys')
    run('rm -f ~/.ssh/new_key')

    @utils.run_as('root')
    def copy_key_root(user_name):
        u"""Копирование ключа для root."""
        print copy_key_root.__doc__
        run('cp -r ~%s/.ssh ~/' % user_name)

    copy_key_root(run('whoami'))

    @utils.run_as('root')
    def disable_password_auth():
        u"""Отключаем возможность авторизации по текстовому паролю."""
        print disable_password_auth.__doc__
        append_line('/etc/ssh/sshd_config', 'PasswordAuthentication no')
        run('service ssh restart')

    if no_password:
        disable_password_auth()


def pip_install(pkg_list):
    u"""
    Установка PIP пакетов.
    """
    options = {
        'virtualenv': env.conf.ENV_DIR,
        'cache': '%s/pip' % CONFIG.get('CACHE_PATH_REMOTE'),
        'pkg_list': pkg_list,
        }
    run('pip install -E %(virtualenv)s --download-cache=%(cache)s %(pkg_list)s' % options)

def sync_back_apt():
    u"""
    Получение APT пакетов в локальный кэш из удалённого.
    """
    HOST, PORT = CONFIG.get('VIRTUALBOX').split(':')
    CMD = '''rsync -e 'ssh -p %s' --verbose --archive --delete %s:/var/cache/apt/archives/*.deb ./caches/apt/'''
    local(CMD % (PORT, HOST))

def sync_back_pip():
    u"""
    Получение PIP пакетов в локальный кэш из удалённого.
    """
    HOST, PORT = CONFIG.get('VIRTUALBOX').split(':')
    CMD = '''rsync -e 'ssh -p %s' --verbose --archive --delete %s:/tmp/pip/* ./caches/pip/'''
    local(CMD % (PORT, HOST))

def sync_back():
    u"""
    Синхронизация (download) кэшей.
    """
    print sync_back.__doc__
    sync_back_apt()
    sync_back_pip()

