=================
Backup & restore
=================

.. _application-backup:

Application backup
==================

Backing up a Geotrek instance involves saving the key components required to restore the application in case of failure.

A complete backup typically includes:

* the database
* the uploaded media files
* the application configuration

Database
--------

The database contains all structured data (treks, POIs, etc.).
It can be exported using the following command:

Database
--------

The database contains all structured data (treks, POIs, etc.).
It can be exported using the following command:

.. code-block:: bash

    sudo -u postgres pg_dump --no-acl --no-owner -Fc geotrekdb > `date +%Y%m%d%H%M`-database.backup

Media files
-------------

Media files include all user-uploaded content such as images and documents.
They are stored in the `media` directory and can be archived as follows:

.. code-block:: bash

    tar -zcvf `date +%Y%m%d%H%M`-media.tar.gz /opt/geotrek-admin/var/media/

Configuration
--------------

The configuration directory contains environment-specific settings required to run the application.
It is recommended to back it up to preserve parameters:

.. code-block:: bash

    tar -zcvf `date +%Y%m%d%H%M`-conf.tar.gz /opt/geotrek-admin/var/conf/

.. note::

   Depending on your setup, you may also want to back up additional elements such as automation scripts (cron).

.. _application-restore:

Application restore
====================

Restoring a Geotrek instance consists in rebuilding the application environment and reloading the previously saved data.

Depending on your setup, this process may involve preparing a new server or reusing an existing one.

Database setup
---------------

If the restoration is performed on a new server, a PostgreSQL/PostGIS environment needs to be available beforehand, along with a database user.

For example:

.. code-block:: bash

    sudo apt install postgresql-14-pgrouting
    sudo -u postgres psql -c "CREATE USER geotrek PASSWORD 'geotrek';"

.. note::

   Installation commands may vary depending on the operating system, PostgreSQL version, and package source (distribution repository or official PostgreSQL repository).

   For instance, on Ubuntu 24.04 (Noble), the following command can be used:

   .. code-block:: bash

      sudo apt install postgresql-17-pgrouting
      sudo -u postgres psql -c "CREATE USER geotrek PASSWORD 'geotrek';"

Database creation
------------------

An empty database must be created before importing the backup.

.. code-block:: bash

    sudo -u postgres psql -c "CREATE DATABASE geotrekdb OWNER geotrek;"
    sudo -u postgres psql -d geotrekdb -c "CREATE EXTENSION postgis;"
    sudo -u postgres psql -d geotrekdb -c "CREATE EXTENSION postgis_raster;"
    sudo -u postgres psql -d geotrekdb -c "CREATE EXTENSION pgcrypto;"
    sudo -u postgres psql -d geotrekdb -c "CREATE EXTENSION pgrouting;"

These extensions are required for Geotrek to work properly.

Database restore
----------------

Once the database is ready, the backup can be restored:

.. code-block:: bash

  pg_restore -U geotrek -h localhost --clean --no-acl --no-owner -d geotrekdb 20200510-geotrekdb.backup

If issues occur during the restore process, recreating a fresh database before retrying can help resolve conflicts.

Media and configuration
------------------------

Media files and configuration should also be restored to ensure the application behaves as expected.

.. code-block:: bash

    tar -zxvf 20200510-media.tar.gz
    tar -zxvf 20200510-conf.tar.gz

Make sure the extracted files are placed in the appropriate directories of your Geotrek installation.

Final steps
-----------

Once all components have been restored, the application can be started following the standard installation procedure.

.. note::

    Follow :ref:`Fresh installation <fresh-installation>` method to use an existing database rather than creating a new one.