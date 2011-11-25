# -*- coding: utf-8 -*-

import sys
from os.path import basename, splitext

def make_config(file_name):
    with open(file_name) as src:
        with open('./configuration.py', 'w') as dst:
            dst.write(src.read())
            dst.close()
        src.close()

def configure(name):
    u"""
    Create settings.py using passed parameter.
    """

    CONFIG = {}
    module = __import__('cfgs.%s' % name)
    CONFIG.update(getattr(module, name).CONFIG)

    from string import Template

    print '\tCreate src/settings.py'
    with open('./tpls/settings.template', 'r') as src:
        with open('./src/settings.py', 'w') as dst:
            template = Template(src.read())
            dst.write(template.substitute(CONFIG))
            dst.close()
        src.close()

    print '\tCreate fabfile/hosts.py'
    with open('./tpls/hosts.template', 'r') as src:
        with open('./fabfile/hosts.py', 'w') as dst:
            CONFIG.update({
                'DB_USER': CONFIG['DATABASES']['default']['USER'],
                'DB_PASSWORD': CONFIG['DATABASES']['default']['PASSWORD'],
                })
            template = Template(src.read())
            dst.write(template.substitute(CONFIG))
            dst.close()
        src.close()

if __name__=="__main__":
    args = sys.argv
    if 2 != len(args):
        print 'Usage:\n\t%s <CONFIG FILE>' % args[0]
        sys.exit(1)
    file_name = args[1]

    print 'Using %s as configuration file.' % file_name
    name, ext = splitext(basename(file_name))
    configure(name)

    print 'Create configuration file.'
    make_config(file_name)

sys.exit(0)
sys.argv
