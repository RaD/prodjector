# -*- coding: utf-8 -*-

from fabric.api import run, put
from fab_deploy import utils

from .utils import CONFIG

def apt_cache_prepare():
    u"""
    Наполнение кэша с системными пакетами.
    """
    print apt_cache_prepare.__doc__
    local_path = CONFIG.get('CACHE_PATH_LOCAL', './caches')
    remote_path = CONFIG.get('CACHE_PATH_REMOTE', '/tmp')
    name = 'apt'
    source = '%s/%s' % (local_path, name)
    destination = '%s/%s' % (remote_path, name)
    run('mkdir -p %s' % destination)
    put(source, remote_path)

    @utils.run_as('root')
    def copy_apt_cache():
        u"""Копирование пакетов в /var/cache/apt."""
        print copy_apt_cache.__doc__
        run('mv %s/*.deb /var/cache/apt/archives/' % destination)

    copy_apt_cache()
    run('rm -rf %s' % destination)

def pip_cache_prepare():
    u"""
    Наполнение кэша с системными пакетами.
    """
    print pip_cache_prepare.__doc__
    local_path = CONFIG.get('CACHE_PATH_LOCAL', './caches')
    remote_path = CONFIG.get('CACHE_PATH_REMOTE', '/tmp')
    name = 'pip'
    source = '%s/%s' % (local_path, name)
    destination = '%s/%s' % (remote_path, name)
    run('mkdir -p %s' % destination)
    put(source, remote_path)

def other_cache_prepare():
    u"""
    Наполнение кэша с остальными данными.
    """
    print other_cache_prepare.__doc__
    local_path = CONFIG.get('CACHE_PATH_LOCAL', './caches')
    remote_path = CONFIG.get('CACHE_PATH_REMOTE', '/tmp')
    name = 'other'
    source = '%s/%s' % (local_path, name)
    destination = '%s/%s' % (remote_path, name)
    run('mkdir -p %s' % destination)
    put(source, remote_path)
