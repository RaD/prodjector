# -*- coding: utf-8 -*-

from fabric.api import env, settings, cd, run
from fabric.contrib import files

from fab_deploy import utils

TYPE = 'SERVICE'
NAME = 'Munin'
APT = ['munin', 'libwww-perl', 'libdbd-pg-perl',]
PIP = []

def deploy():
    u"""
    Deploy Munin...
    """
    print u'Munin is installed on OS level.'

@utils.run_as_sudo
def setup():
    u"""
    Setup Munin...
    """
    print setup.__doc__
    _make_cfg()
    _plugins_default()

@utils.run_as_sudo
def final():
    u"""
    Run Munin...
    """
    print final.__doc__
    _restart()

@utils.run_as_sudo
def _restart():
    u"""Restarts the munin-node daemon."""
    run('service munin-node restart')

@utils.run_as_sudo
def _make_cfg():
    u"""Create munin's confgiuration files."""
    base_dir = '/etc/munin'
    files.upload_template('./tpls/munin_base.template',
                          '%s/%s' % (base_dir, 'munin.conf'),
                          env.conf, use_jinja=True)
    files.upload_template('./tpls/munin_node.template',
                          '%s/%s' % (base_dir, 'munin-node.conf'),
                          env.conf, use_jinja=True)
    files.upload_template('./tpls/munin_plugin_node.template',
                          '%s/%s' % (base_dir, 'plugin-conf.d/munin-node'),
                          env.conf, use_jinja=True)

def _plugins_default(restart=False):
    u"""Enables a predefined set of plugins, disables the rest."""
    DEFAULT_PLUGINS = [
        #'apache_accesses',
        #'apache_processes',
        #'apache_volume',
        'cpu',
        'df',
        'diskstats',
        #'exim_mailqueue',
        #'exim_mailstats',
        'if_eth0',
        'iostat',
        'load',
        'memory',
        'munin_stats',
        #'nginx_request',
        #'nginx_status',
        'postgres_connections_' + env.conf.DB_NAME,
        'postgres_locks_' + env.conf.DB_NAME,
        'postgres_querylength_' + env.conf.DB_NAME,
        'postgres_scans_' + env.conf.DB_NAME,
        'postgres_size_' + env.conf.DB_NAME,
        'postgres_transactions_' + env.conf.DB_NAME,
        'postgres_users',
        'postgres_xlog',
        'processes',
        'swap',
        'threads',
        'vmstat',
        ]
    _plugins_disable_all()
    _plugins_enable(*DEFAULT_PLUGINS)
    if restart:
        _restart()

@utils.run_as_sudo
def _plugins_disable_all(restart=False):
    u"""Removes all plugins from the node configuration."""
    run('rm -f /etc/munin/plugins/*')
    if restart:
        munin_restart()

@utils.run_as_sudo
def _plugins_enable(*plugins, **kwargs):
    u"""Adds specified bundled plugins to the node configuration."""
    for plugin in plugins:
        orig_file = '/usr/share/munin/plugins/' + plugin
        if not files.exists(orig_file):
            # trying to guess a wildcard plugin file name
            orig_file = orig_file.rsplit('_', 1)[0] + '_'
            if not files.exists(orig_file):
                continue
        run('ln -sf "%s" "/etc/munin/plugins/%s"' % (orig_file, plugin))
    if kwargs.get('restart', False):
        _restart()

