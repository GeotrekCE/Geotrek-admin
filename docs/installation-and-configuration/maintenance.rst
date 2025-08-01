===========
Maintenance
===========

.. _maintenance:

Maintenance mode
================

If you want to block access to your application while you are performing maintenance tasks, you can activate the maintenance mode.
This will display a message to users indicating that the application is temporarily unavailable.

.. md-tab-set::
    :name: maintenance-mode

    .. md-tab-item:: With Debian

            .. code-block:: bash

                sudo geotrek maintenance_mode on # activate maintenance mode
                sudo geotrek maintenance_mode off # deactivate maintenance mode

    .. md-tab-item:: With Docker

         .. code-block:: bash

                docker compose run --rm web ./manage.py maintenance_mode on # activate maintenance mode
                docker compose run --rm web ./manage.py maintenance_mode off # deactivate maintenance mode

.. _application-backup:

Application backup
==================

Database

.. code-block:: bash

    sudo -u postgres pg_dump --no-acl --no-owner -Fc geotrekdb > `date +%Y%m%d%H%M`-database.backup

Media files

.. code-block:: bash

    tar -zcvf `date +%Y%m%d%H%M`-media.tar.gz /opt/geotrek-admin/var/media/

Configuration

.. code-block:: bash

    tar -zcvf `date +%Y%m%d%H%M`-conf.tar.gz /opt/geotrek-admin/var/conf/

.. _application-restore:

Application restore
====================

If you restore Geotrek-admin on a new server, you will have to install PostgreSQL and PostGIS and create a database user first.
Otherwise go directly to the database creation step.

.. code-block:: bash

    sudo apt install postgresql-14-pgrouting
    sudo -u postgres psql -c "CREATE USER geotrek PASSWORD 'geotrek';"


.. note::
  The installation command will never be the same depending on the servers hosting the database (Ubuntu 22, 24 / official repository / PostgreSQL repository / RedHat, etc.). 
  
  Here is an example with the command to run to install PostgreSQL on Ubuntu 24.0 (Noble) :

  .. code-block:: bash

      sudo apt install postgresql-17-pgrouting
      sudo -u postgres psql -c "CREATE USER geotrek PASSWORD 'geotrek';"

Create an empty database (``geotrekdb`` in this example):

.. code-block:: bash

    sudo -u postgres psql -c "CREATE DATABASE geotrekdb OWNER geotrek;"
    sudo -u postgres psql -d geotrekdb -c "CREATE EXTENSION postgis;"
    sudo -u postgres psql -d geotrekdb -c "CREATE EXTENSION postgis_raster;"
    sudo -u postgres psql -d geotrekdb -c "CREATE EXTENSION pgcrypto;"
    sudo -u postgres psql -d geotrekdb -c "CREATE EXTENSION pgrouting;"

Restore backup:

.. code-block:: bash

    pg_restore -U geotrek -h localhost --clean --no-acl --no-owner -d geotrekdb 20200510-geotrekdb.backup

If errors persist, rename your database and recreate a fresh one, then restore.

Extract media and configuration files:

.. code-block:: bash

    tar -zxvf 20200510-media.tar.gz
    tar -zxvf 20200510-conf.tar.gz

Follow *Fresh installation* method. Choose to manage database by yourself.

.. _postgresql-optimization:

PostgreSQL optimization
=======================

* Increase ``shared_buffers`` and ``work_mem`` according to your RAM

* `Log long queries <http://wiki.postgresql.org/wiki/Logging_Difficult_Queries>`_

* Use `pg activity <https://github.com/julmon/pg_activity#readme>`_ for monitoring

.. _access-your-database-securely-on-your-local-machine-qgis:

Access your database securely on your local machine (QGIS)
==========================================================

Instead of opening your database to the world (by opening the 5432 port for
example), you can use `SSH tunnels <https://www.postgresql.org/docs/current/ssh-tunnels.html>`_. Follow `this tutorial <https://makina-corpus.com/devops/acceder-base-donnees-postgresql-depuis-qgis-pgadmin-securisee>`_ for more information (in french).

.. _manage-cache:

Manage Cache
============

You can purge application cache :

- with command line :

.. md-tab-set::
    :name: purge-cache-tabs

    .. md-tab-item:: With Debian

         .. code-block:: bash

            sudo geotrek clearcache 

    .. md-tab-item:: With Docker

         .. code-block:: python
    
          docker compose run --rm web ./manage.py clearcache 

- in Geotrek-admin interface : ``https://<server_url>/admin/clearcache/``