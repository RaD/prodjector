ProDJector
==========

This is simple skeleton for Django powered project.

Initialization
--------------

First of all, create the project structure with::

  ./init.sh

It does the following:

* create virtual environment;
* create cache directories;
* install python packeges for dev environment;
* create directory for your sources.

Fill the ``src`` directory with your source code. I do this with
symbolic links.

Configuration
-------------

Look at ``cfgs/demo.py``. There is simple Python dictionary with
configuration parameters. Copy this file and edit the settings there.

Open the ``tpls/settings.template`` and insert there code from your
original ``settings.py`` using ``${}`` for the configuration
parameters.

Now you're ready to configure the project. Do::

  python fabfile/configure.py cfgs/<YOUR_CONFIG_FILE>

This will create ``src/settings.py`` and ``fabfile/hosts.py`` files.

Deployment
----------

Now you can deploy your project::

  fab autodiscover deploy

where ``autodiscover`` -- check the dependency information from fabric
plugins (see ``fabfile/`` directory).
