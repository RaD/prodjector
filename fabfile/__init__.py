# -*- coding: utf-8 -*-

from .caches import apt_cache_prepare, pip_cache_prepare, other_cache_prepare
from .utils import CONFIG, setup_key_auth, pip_install, sync_back
from .hosts import virtualbox
from .postgres import setup as pgsetup

from fabric.api import settings, local, put
from fab_deploy import system, utils, virtualenv

PRIORITY = ('DATABASE', 'COMPONENT', 'SERVICE',)
PACKAGES = {}
APT = []
PIP = []

def deploy(install_key='yes', no_password='yes', fill_cache='yes', use_cache='yes'):
    u"""
    Функция обеспечивает развёртывание проекта.

    * install_key - установить открытый ключ для SSH;
    * no_password - запретить авторизацию по паролям;
    * fill_cache - наполнить кэши;
    * use_cache - использовать кэши.
    """
    kwargs = {}

    if 'yes' == install_key:
        setup_key_auth(no_password)
    if 'yes' == fill_cache:
        # заполняем кэши
        other_cache_prepare()
        apt_cache_prepare()
        pip_cache_prepare()
    if 'yes' == use_cache:
        # собираем путь до PIP кэша на целевой машине
        remote_path = CONFIG.get('CACHE_PATH_REMOTE', '/tmp')
        kwargs['cache'] = '%s/%s' % (remote_path, 'pip')

    autodiscover()
    #deploy_prepare()

    # последовательно проходим по всем пакетам в порядке приоритета и
    # действия
    for action in ('deploy', 'setup', 'final'):
        for priority in PRIORITY:
            for title, module in PACKAGES.get(priority, {}).items():
                if hasattr(module, action):
                    getattr(module, action)()

    print '=-='*20
    print '''Run 'python manage.py createsuperuser'.'''
    print '=-='*20

def deploy_plugin(name, priority):
    u"""
    Функция для развёртывания указанного плагина.
    """
    print deploy_plugin.__doc__
    autodiscover()

    print PACKAGES

    if priority not in PRIORITY:
        raise RuntimeError(u'Wrong PRIORITY!')
    for action in ('deploy', 'setup', 'final'):
        module = PACKAGES[priority][name]
        if hasattr(module, action):
            getattr(module, action)()

def autodiscover():
    u"""
    Функция получения информации о пакетах.
    """
    print autodiscover.__doc__
    global PACKAGES, APT, PIP

    prodjector = CONFIG.get('PRODJECTOR')
    if not prodjector:
        raise(u'Define PRODJECTOR section in the configuration file.')

    for name in prodjector.get('PLUGINS', ()):
        module = getattr(__import__('fabfile.%s' % name), name)
        APT += module.APT
        PIP += module.PIP
        category = PACKAGES.get(module.TYPE, {})
        category[module.NAME] = module
        PACKAGES[module.TYPE] = category

    for priority in PRIORITY:
        category = PACKAGES.get(priority, {})
        print '{0:<10}: {1:<60}'.format(priority, ', '.join(category.keys()))
    print '{0:<10}: {1:<60}'.format('APT', ', '.join(APT))
    print '{0:<10}: {1:<60}'.format('PIP', ', '.join(PIP))
    print

def deploy_prepare():
    u"""
    Подготовка удалённого сервера к установке ПО.
    """
    print deploy_prepare.__doc__
    # устанавливаем sudo, настраиваем backports
    system.prepare_server()

    # создаём виртуальное окружение
    virtualenv.virtualenv_create()

    # устанавливаем APT и PIP пакеты
    packages = ' '.join(APT)
    system.aptitude_install(packages)
    packages = ' '.join(PIP)
    pip_install(packages)

    # устанавливаем общие зависимости
    put('./reqs', '~/')
    pip_install('-r reqs/apps.txt')

    # перекидываем код на сервер
    rsync_codebase()

def rsync_codebase():
    u"""
    Синхронизация исходного кода.
    """
    print rsync_codebase.__doc__
    VIRTUALBOX = CONFIG.get('VIRTUALBOX')
    if not VIRTUALBOX:
        raise u'Check VIRTUALBOX parameter.'
    HOST, PORT = VIRTUALBOX.split(':')
    CMD = '''rsync -e 'ssh -p %s' --copy-links --recursive --verbose ./src/* %s:src/zina/'''
    local(CMD % (PORT, HOST))
