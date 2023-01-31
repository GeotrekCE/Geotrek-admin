============
Installation
============

Use these instructions to install Geotrek-admin in an easy way on a dedicated Ubuntu Focal Fossa 20.04 LTS server for production.
For another distributions, please use :ref:`the Docker installation method <docker-section>`. It requires more technical skills.
Lastly, for a developer instance, please follow :ref:`the dedicated procedure <development-section>`.


Requirements
------------

A first estimation of minimal required system resources are:

* 2 cores
* 4 Go RAM
* 20 Go disk space

For big instances required system resources are:

* 4 cores
* 8 Go RAM or more
* 50 Go disk space or more (20 Go + estimated size of attached files like photos, including elements imported from SIT)

Software requirements are :

* Ubuntu Focal Fossa 20.04 LTS. Server flavor is recommended but any other flavors work too (desktop…)

An Internet connection with open HTTP and HTTPS destination ports is required.


Information to prepare before installation
------------------------------------------

These information will be asked during the installation process and are the basic configuration of Geotrek-admin:

* The **domain name** or **IP** to use to access to **Geotrek-admin** web application.
* Rando server name: the **domain name** to use to access to **Geotrek-rando** website (optional, if appropriate).
* PostgreSQL **host, port, user, password and DB name** if you use an external DB server.
* The **SRID** of the projection to use to store geometries. The projection must match your geographic area and coordinates must be in meters.
* The list of **languages** into which translation of contents will be made
* The name or acronym of your **organization**


Fresh installation
------------------

Run the following command in a shell prompt on your server:

::

   curl https://raw.githubusercontent.com/GeotrekCE/Geotrek-admin/master/tools/install.sh | bash

If you don't want to use a local database, you can run the following command instead.
This will prevent the script to install PostgreSQL server locally.
Don't forget to enable PostGIS extension in your remote database before installation.

::

   curl https://raw.githubusercontent.com/GeotrekCE/Geotrek-admin/blob/master/tools/install.sh | bash -s - --nodb

Then create the application administrator account and connect to the web interface.

::

   sudo geotrek createsuperuser

If you are not confident with the ``install.sh`` script, or if you are having troubles, you can do the same operations by hand:

1. Add ``deb https://packages.geotrek.fr/ubuntu bionic main`` to APT sources list.
2. Add https://packages.geotrek.fr/geotrek.gpg.key to apt keyring.
3. Run ``apt-get update``
4. If you want to use a local database, install PostGIS package (before installing Geotrek-admin, not at the same time).
   If not, you must create database and enable PostGIS extension before.
5. Install the Geotrek-admin package (``sudo apt install geotrek-admin``).

.. note ::

    Geotrek-admin is automatically installed in ``/opt/geotrek-admin/`` directory.

    The installation automatically creates an internal ``geotrek`` linux user, owner of this directory

    The Geotrek-admin Python application is located in ``/opt/geotrek-admin/lib/python3.6/site-packages/geotrek`` directory


Upgrade
-------

From Geotrek-admin >= 2.33
~~~~~~~~~~~~~~~~~~~~~~~~~~

To upgrade the whole server, including Geotrek-admin, run:

::

   sudo apt-get update
   sudo apt-get upgrade

If your current version is <= 2.40.1 you should run instead:

::

   sudo apt-get update  --allow-releaseinfo-change
   sudo apt-get upgrade

To prevent upgrading Geotrek-admin with the whole distribution, you can run:

::

   sudo apt-mark hold geotrek-admin

To upgrade only Geotrek-admin and its dependencies, run:

::

   sudo apt-get install geotrek-admin


From Geotrek-admin <= 2.32
~~~~~~~~~~~~~~~~~~~~~~~~~~

First of all, make sure your current Geotrek-admin version works correctly.
Especially, after an upgrade of the Ubuntu distribution, you will have to run ``./install.sh``
before proceeding with Geotrek-admin upgrade.

Then, go inside your existing Geotrek-admin installation directory and run the dedicated migration script:

::

   curl https://raw.githubusercontent.com/GeotrekCE/Geotrek-admin/blob/master/tools/migrate.sh | bash


Check if ``SPATIAL_EXTENT`` is well set in ``/opt/geotrek-admin/var/conf/custom.py`` (see Advanced configuration section)

.. note ::

    Geotrek-admin is now automatically installed in ``/opt/geotrek-admin/`` directory
    and the advanced configuration file moved to ``/opt/geotrek-admin/var/conf/custom.py``
    (with spatial extent, map and modules configuration...).

    See advanced configuration documentation for details.

    The ``etc/settings.ini`` file is replaced by basic configuration, updated with
    ``sudo dpkg-reconfigure geotrek-admin`` command (database, SRID, languages, server_name, timeout...).

    Update your imports, synchronization and backup commands and directories.


From Geotrek-admin <= 2.69.0
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**WARNING!**

Starting from version 2.70.0, Geotrek now needs PostgreSQL extension 'pgrypto'.

Make sure to run the following command **BEFORE** upgrading:

``su postgres -c "psql -q -d $POSTGRES_DB -c 'CREATE EXTENSION pgcrypto;'"``


Server migration
----------------

It is a new installation with an additional backup/restore and a file transfert in between. The commands below are examples to adapt to your actual configuration (server names, database configuration). These commands apply to versions >= 2.33. If your version is below 2.33, please check the doc of your version.

Backup settings, media files and database on the old server:

::

    sudo -u postgres pg_dump -Fc geotrekdb > geotrekdb.backup
    tar cvzf data.tgz geotrekdb.backup /opt/geotrek-admin/var/conf/ /opt/geotrek-admin/var/media/

Restore files on the new server:
::

    scp old_server_ip:path/to/data.tgz .
    tar xvzf data.tgz


Ubuntu bionic PostGIS 2.5 upgrade
---------------------------------

Geotrek-admin requires at least PostGIS 2.5.

If you installed Geotrek-admin on bionic ubuntu with provided install method, you should update your database :
::

    # Firstly, backup your database (see previous section)
    # install postgresql APT repository
    # (from https://wiki.postgresql.org/wiki/Apt)

    sudo apt install curl ca-certificates gnupg
    curl https://www.postgresql.org/media/keys/ACCC4CF8.asc | gpg --dearmor | sudo tee /etc/apt/trusted.gpg.d/apt.postgresql.org.gpg >/dev/null
    sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
    sudo apt update

    # install postgis 2.5 on postgresql 10
    sudo apt install postgresql-10-postgis-2.5-scripts
    sudo -u postgres psql -d geotrekdb -c "ALTER EXTENSION POSTGIS UPDATE";  # replace geotrekdb by your database name

    # You database is now using postgis 2.5 !

    # Troubleshooting
    # If you encounter error with last command to update postgis, just drop view v_projects and retry
    # This view will be recreated after next Geotrek-admin upgrade or dpkg-reconfigure.
    sudo -u postgres psql -d geotrekdb -c "DROP VIEW v_projects;";
    sudo -u postgres psql -d geotrekdb -c "ALTER EXTENSION POSTGIS UPDATE";

    # Warning, by using postgresql official apt repo, next apt upgrade or apt full-upgrade will install postgresql-9.6 and postgis 3 along your database, because postgis meta-package has changed
    # If your are not using postgresql-9.6, you can remove it (bionic postgresql default version is 10)
    # sudo apt remove postgresql-9.6

If you use an external database, you should adapt this method along your system



Uninstallation
--------------

Run:

::

   apt-get remove geotrek-admin

Media files will be left in ``/opt/geotrek-admin/var`` directory. To remove them, run:

::

   apt-get purge geotrek-admin

To remove dependencies (convertit, screamshooter…), run:

::

   apt-get autoremove

.. note ::

    PostgreSQL and its database will not be removed by these commands. If need be, remove them manually.
