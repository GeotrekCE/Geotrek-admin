===========
Maintenance
===========


Operating system updates
------------------------

.. code-block:: bash

    sudo apt-get update
    sudo apt-get dist-upgrade


Application backup
------------------

Database

.. code-block:: bash

    sudo -u postgres pg_dump --no-acl --no-owner -Fc geotrekdb > `date +%Y%m%d%H%M`-database.backup

Media files

.. code-block:: bash

    tar -zcvf `date +%Y%m%d%H%M`-media.tar.gz /opt/geotrek-admin/var/media/

Configuration

.. code-block:: bash

    tar -zcvf `date +%Y%m%d%H%M`-conf.tar.gz /opt/geotrek-admin/var/conf/


Application restore
-------------------

If you restore Geotrek-admin on a new server, you will have to install PostgreSQL and PostGIS and create a database user first.
Otherwise go directly to the database creation step.

Example for Ubuntu 18:

.. code-block:: bash

    sudo apt install postgresql-10 postgresql-10-postgis-2.5
    sudo -u postgres psql -c "CREATE USER geotrek PASSWORD 'geotrek';"


Create an empty database (``geotrekdb`` in this example):

.. code-block:: bash

    sudo -u postgres psql -c "CREATE DATABASE geotrekdb OWNER geotrek ENCODING 'UTF8' TEMPLATE template0;"
    sudo -u postgres psql -d geotrekdb -c "CREATE EXTENSION postgis;"
    sudo -u postgres psql -d geotrekdb -c "CREATE EXTENSION postgis_raster;"
    sudo -u postgres psql -d geotrekdb -c "CREATE EXTENSION pgcrypto;"


Restore backup:

.. code-block:: bash

    sudo -u postgres pg_restore -d geotrekdb 20200510-geotrekdb.backup

If errors occurs on restore, try to add ``--clean`` option.

If errors persists, rename your database and recreate a fresh one, then restore.

Extract media and configuration files:

.. code-block:: bash

    tar -zxvf 20200510-media.tar.gz
    tar -zxvf 20200510-conf.tar.gz

Follow *Fresh installation* method. Choose to manage database by yourself.


PostgreSQL optimization
-----------------------

* Increase ``shared_buffers`` and ``work_mem`` according to your RAM

* `Log long queries <http://wiki.postgresql.org/wiki/Logging_Difficult_Queries>`_

* Use `pg activity <https://github.com/julmon/pg_activity#readme>`_ for monitoring


Access your database securely on your local machine (QGIS)
----------------------------------------------------------

Instead of opening your database to the world (by opening the 5432 port for
example), you can use `SSH tunnels <http://www.postgresql.org/docs/9.3/static/ssh-tunnels.html>`_.


Major evolutions from version 2.33
----------------------------------

From version 2.33, Geotrek-admin is packaged in a debian package. This mean several things :

- a system user ``geotrek`` is created on install ;

- base code is located in ``/opt/geotrek-admin`` folder ;

- ``geotrek`` is the new command, replacing ``bin/django``, and must be run in root (system user ``geotrek`` is used after) ;

- there is no more ``settings.ini`` but an ``env`` file with environment variables ;

- configuration files (custom.py et env), parsers and all customisation files (templates and translations) are now located in ``/opt/geotrek-admin/var/conf`` ;

- we advise you to configure data synchronization in ``/opt/geotrek-admin/var``
