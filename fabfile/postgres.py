# -*- coding: utf-8 -*-

from __future__ import with_statement
from datetime import datetime
import posixpath

from fabric.api import *
from fabric.utils import puts
from fabric.contrib import console, files

from fab_deploy import utils, system
from fab_deploy.mysql import _credentials

TYPE = 'DATABASE'
NAME = 'PostgreSQL'
APT = ['gdal-bin', 'postgresql-8.4-postgis', 'postgresql-server-dev-8.4',]
PIP = ['psycopg2==2.4.1',]

POSTGRES_SUPERUSER = 'postgres'

POSTGRES_CREATE_USER = """
CREATE USER %(db_user)s WITH CREATEDB PASSWORD '%(db_password)s';
"""
POSTGRES_CREATE_DB = """
CREATE DATABASE %(db_name)s OWNER %(db_user)s ENCODING 'UTF8' TEMPLATE %(template)s;
"""

def deploy():
    u"""
    Установка PostgreSQL...
    """
    print u'PostgreSQL is installed on OS level.'

def setup():
    u"""
    Настройка PostgreSQL...
    """
    print setup.__doc__
    with settings(warn_only=True):
        db_name, db_user, _ = _credentials(None, None, None)
        output = run('psql --user %s -c "select 1;" > /dev/null' % db_user)
        if not output.succeeded:
            postgres_create_user()
            postgres_create_postgis_db()

def _is_installed():
    with settings(warn_only=True):
        output = run('psql -V')
    return output.succeeded

def postgres_execute(sql, user=None, password=None):
    """ Executes passed sql command using postgres shell. """
    user = user or env.conf.DB_USER
    if password is None and user != POSTGRES_SUPERUSER:
        password = env.conf.DB_PASSWORD

    pwd_cmd = 'set PGPASSWORD="%s";' % password if password is not None else ''
    sql = sql.replace('"', r'\"')
    cmd = 'psql --user="%s" --command "%s"' % (user, sql,)

    # TODO: superuser password auth?
    if user == POSTGRES_SUPERUSER:
        return sudo(cmd, user=user)
    return run(pwd_cmd + cmd)


@utils.run_as_sudo
def postgres_create_user(db_user=None, db_password=None):
    """ Creates PostgreSQL user. """
    _, db_user, db_password = _credentials(None, db_user, db_password)
    sql = POSTGRES_CREATE_USER % dict(db_user=db_user, db_password=db_password)
    postgres_execute(sql, POSTGRES_SUPERUSER)


@utils.run_as_sudo
def postgres_create_db(db_name=None, db_user=None, template='template1'):
    """ Creates an empty PostgreSQL database. """
    db_name, db_user, _ = _credentials(db_name, db_user, None)
    sql = POSTGRES_CREATE_DB % dict(db_name=db_name, db_user=db_user, template=template)
    postgres_execute(sql, POSTGRES_SUPERUSER)


@utils.run_as_sudo
def postgres_drop_db(db_name, confirm=True):
    question = "Really drop database %s?" % db_name
    if confirm and not console.confirm(question, default=False):
        return
    postgres_execute("DROP DATABASE %s;" % db_name, POSTGRES_SUPERUSER)

@utils.run_as_sudo
@utils.inside_src
def postgres_create_postgis_template():
    """ Installs postgis database template """
    postgis_path = '/usr/share/postgresql/8.4/contrib/postgis-1.5'

    def psql(sql=None, file=None, template='template_postgis'):
        CMD = ['psql -d %s' % template,]
        if sql:
            CMD.append('-c "%s"' % sql)
        elif file:
            CMD.append('-f "%s"' % file)
        sudo(' '.join(CMD), user=POSTGRES_SUPERUSER)

    if files.exists(postgis_path):
        sudo('createdb -E UTF8 template_postgis', user=POSTGRES_SUPERUSER)
        sudo('createlang -d template_postgis plpgsql', user=POSTGRES_SUPERUSER)
        psql(sql='''UPDATE pg_database SET datistemplate='true' WHERE datname='template_postgis';''',
             template='postgres')
        psql(file='%s/%s' % (postgis_path, 'postgis.sql'))
        psql(file='%s/%s' % (postgis_path, 'spatial_ref_sys.sql'))
        psql(sql='GRANT ALL ON geometry_columns TO PUBLIC;')
        psql(sql='GRANT ALL ON spatial_ref_sys TO PUBLIC;')
        psql(sql='GRANT ALL ON geography_columns TO PUBLIC;')

def postgres_create_postgis_db(db_name=None, db_user=None):
    """ Creates empty PostGIS-enabled database """
    with settings(warn_only=True):
        if not files.exists('postgis.installed'):
            postgres_create_postgis_template()
            run('touch postgis.installed')
            postgres_create_db(db_name, db_user, 'template_postgis')

def postgres_dump(dir=None, db_name=None, db_user=None, db_password=None):
    """ Runs pg_dump. Result is stored at <env>/var/backups/ """
    if dir is None:
        dir = env.conf.ENV_DIR + '/var/backups'
        run('mkdir -p ' + dir)

    db_name, db_user, db_password = _credentials(db_name, db_user, db_password)

    now = datetime.now().strftime('%Y.%m.%d-%H.%M')
    filename = '%s%s.sql' % (db_name, now)

    # if dir is absolute then PROJECT_DIR won't affect result path
    # otherwise dir will be relative to PROJECT_DIR
    full_name = posixpath.join(env.conf.PROJECT_DIR, dir, filename)

    run('PGPASSWORD="%s" pg_dump --username="%s" %s | gzip -3 > %s.gz' % (
                        db_password, db_user, db_name, full_name))
