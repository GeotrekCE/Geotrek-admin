=======
Upgrade
=======

.. contents::
   :local:
   :depth: 2


From Geotrek-admin >= 2.33
~~~~~~~~~~~~~~~~~~~~~~~~~~

Beforehand you should update your system's catalog:

::

   sudo apt-get update

If your current version is <= 2.40.1 you should run instead:

::

   sudo apt-get update  --allow-releaseinfo-change

To display the installed version and the latest upgradeable version, run:

::

   apt list --all-versions geotrek-admin

To upgrade only geotrek-admin and its dependencies, run:

::

   sudo apt-get install geotrek-admin

.. note::

   - It is only possible to install the latest version of geotrek-admin via this command line
   - All package versions remain available as `release assets <https://github.com/GeotrekCE/Geotrek-admin/releases/>`_. Download the .deb for your architecture and do ``sudo apt-get install <the .deb package>``.
   - Example : ``sudo apt-get install geotrek-admin_2.106.0.ubuntu20.04_amd64.deb``

Once geotrek-admin has been upgraded you may want to prevent unwanted upgrade with the whole distribution, you can run:

::

   sudo apt-mark hold geotrek-admin


From Geotrek-admin < 2.33
~~~~~~~~~~~~~~~~~~~~~~~~~~

First of all, make sure your current Geotrek-admin version works correctly.
Especially, after an upgrade of the Ubuntu distribution, you will have to run ``./install.sh``
before proceeding with Geotrek-admin upgrade.

Then, go inside your existing Geotrek-admin installation directory and run the dedicated migration script:

::

   curl https://raw.githubusercontent.com/GeotrekCE/Geotrek-admin/blob/master/tools/migrate.sh | bash


Check if ``SPATIAL_EXTENT`` is well set in ``/opt/geotrek-admin/var/conf/custom.py`` (see Advanced configuration section)

.. note::

    Geotrek-admin is now automatically installed in ``/opt/geotrek-admin/`` directory
    and the advanced configuration file moved to ``/opt/geotrek-admin/var/conf/custom.py``
    (with spatial extent, map and modules configuration...).

    See advanced configuration documentation for details.

    The ``etc/settings.ini`` file is replaced by basic configuration, updated with
    ``sudo dpkg-reconfigure geotrek-admin`` command (database, SRID, languages, server_name, timeout...).

    Update your imports, synchronization and backup commands and directories.


From Geotrek-admin < 2.70.0
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**WARNING!**

Starting from version 2.70.0, Geotrek now needs PostgreSQL extension 'pgrypto'.

Make sure to run the following command **BEFORE** upgrading:

``su postgres -c "psql -q -d $POSTGRES_DB -c 'CREATE EXTENSION pgcrypto;'"``


From Geotrek-admin < 2.113.0
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**WARNING!**

Starting from version 2.113.0, Geotrek now requires pgRouting. Please follow these steps before updating.

If you use Ubuntu Bionic 18.04 on your database host (on same or external geotrek-admin host), you can follow the instructions below :ref:`Install pgrouting bionic`.

**On Debian packaging >= Ubuntu Focal 20.04 installation with database on same host:**

1. Backup your database : see `Maintenance <https://geotrek.readthedocs.io/en/latest/install/maintenance.html#application-backup>`_.

2. Install the pgRouting package from your distribution's package manager (if you installed Geotrek using the `install script <https://geotrek.readthedocs.io/en/latest/install/installation.html#fresh-installation>`_ : ``sudo apt install postgresql-pgrouting``).

3. Activate the extension in your database : ``su postgres -c "psql -q -d $POSTGRES_DB -c 'CREATE EXTENSION pgrouting;'"``

4. Update Geotrek as usual

**On a external database host: (Ubuntu >= 20.04 or docker with external database)**

These instructions could be the same as previous if you use a debian like distribution on your database host.

1. Backup your database.
2. Install pgrouting version corresponding to your PostgreSQL version on your database server. (see `pgRouting documentation <https://docs.pgrouting.org/latest/en/index.html>`_).
3. Enable pgrouting extension in your geotrek database with your database superuser.

**On a Docker installation: (if your database is a docker container)**

1. Backup your database : ``docker compose run --rm web bash -c 'pg_dump --no-acl --no-owner -Fc -h postgres $POSTGRES_DB > `date +%Y%m%d%H%M`-database.backup'``

2. Replace the docker image in ``docker-compose.yml`` for service ``postgres`` with an image that includes PostgreSQL, PostGIS and pgRouting version >=3.0.0 (`example with PostgreSQL 12, PostGIS 3.0 and pgRouting 3.0.0 <https://hubgw.docker.com/layers/pgrouting/pgrouting/12-3.0-3.0.0/images/sha256-382a2862cac07b0d3e57be9ddac587ad7a0d890ae2adc9fbae96a320a50194fb>`_). We highly recommend picking an image including the **same versions of PostgreSQL and PostGIS that you already use**. If you choose to pick later versions instead, you will need to delete your database, recreate it, and use ``pg_restore`` to restore the backup from step 1 (see "Recreate user and database" below).

3. Update Geotrek as usual


Server migration
~~~~~~~~~~~~~~~~

It is a new installation with an additional backup/restore and a file transfert in between. The commands below are examples to adapt to your actual configuration (server names, database configuration). These commands apply to versions >= 2.33. If your version is below 2.33, please check the doc of your version.

Backup settings, media files and database on the old server:

::

    sudo -u postgres pg_dump -Fc geotrekdb > geotrekdb.backup
    tar cvzf data.tgz geotrekdb.backup /opt/geotrek-admin/var/conf/ /opt/geotrek-admin/var/media/

Restore files on the new server:

::

    scp old_server_ip:path/to/data.tgz .
    tar xvzf data.tgz


PostgreSQL
~~~~~~~~~~

Geotrek-admin support PostgreSQL 12+, PostGIS 2.5+ and PgRouting 3.0+ for now.
We recommend to upgrade to PostgreSQL 16, PostGIS 3.4 and PgRouting 3.7.

You can check your versions with the following command:

::

   sudo geotrek check_versions


If your PostgreSQL version is below 12, you should upgrade your PostgreSQL server.
If you can not upgrade for the moment, check release notes before each Geotrek-admin upgrade to ensure compatibility.
You will be able to mark hold your Geotrek-admin Ubuntu package to prevent unwanted upgrade.

::

   sudo apt-mark hold geotrek-admin


In case of unwanted upgrade, you will be able to revert your Geotrek-admin version to last supporting PostgreSQL 10 with, for example:


::

   sudo apt-get install geotrek-admin=2.102.1.ubuntu20.04


for Ubuntu 20.04, or

::

   sudo apt-get install geotrek-admin=2.102.1.ubuntu18.04


for Ubuntu bionic


Update PostgreSQL / PostGIS / PgRouting on Ubuntu Bionic
--------------------------------------------------------

.. warning::

    Ubuntu Bionic is already deprecated. We recommend you to install PostgreSQL on a dedicated server, with a most recent version of Ubuntu.
    If possible, on the same host or datacenter than your Geotrek-admin instance.
    If you can't, you can follow these instructions to upgrade PostgreSQL, PostGIS and PgRouting on Ubuntu Bionic with official PostgreSQL APT archive repository.
    The ultimate version published for Bionic is PostgreSQL 14, supported until November 12, 2026.


I you have Postgresql < 14:

::

    sudo rm -f /etc/apt/sources.list.d/pgdg.list
    sudo apt install curl ca-certificates
    sudo install -d /usr/share/postgresql-common/pgdg
    sudo curl -o /usr/share/postgresql-common/pgdg/apt.postgresql.org.asc --fail https://www.postgresql.org/media/keys/ACCC4CF8.asc
    sudo sh -c 'echo "deb [signed-by=/usr/share/postgresql-common/pgdg/apt.postgresql.org.asc] https://apt-archive.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
    sudo apt update


Then, make a database dump. You can see user / database / password in /opt/geotrek-admin/conf/env file.

::

    sudo -u postgres pg_dump -Fc --no-acl --no-owner -d <your geotrek database name> > ./backup.dump


Now, install newest version of PostgreSQL and PostGIS:

::

    sudo apt install postgresql-14-postgis-3



.. note::

    Installing many PostgreSQL versions on the same system will use another port than default 5432.
    You can check the newest port with ``pg_lsclusters`` command. For next lines, we consider new port is 5433.


Recreate user and database:


::

    sudo -u postgres psql -p 5433


::

    CREATE USER <your geotrek user> WITH ENCRYPTED PASSWORD '<your geotrek user password>';
    CREATE DATABASE <your geotrek database> WITH OWNER <your geotrek user>;
    \c <your geotrek database>
    CREATE EXTENSION postgis;
    CREATE EXTENSION postgis_raster;
    CREATE EXTENSION pgcrypto;
    \q

.. warning::

    You should report configuration from ``/etc/postgresql/10/main/pg_hba.conf`` to ``/etc/postgresql/14/main/pg_hba.conf``.
    Then restart your PostgreSQL

    ::

        sudo cp /etc/postgresql/10/main/pg_hba.conf /etc/postgresql/14/main/pg_hba.conf
        sudo systemctl restart postgresql


You can now restore your database dump.


::

    pg_restore -h 127.0.0.1 -p 5433 -U <your geotrek user> -d <your geotrek database> ./backup.dump

.. note::

    Note you have to use ``-h 127.0.0.1`` to connect with the ``geotrek`` user (this user cannot connect with the default unix socket). Connecting with ``geotrek`` is important for restored entities to have the right owner.
    Some errors can occurs, around extensions creation or ``spatial_ref_sys`` table content.
    This is normal. We already create these extensions on previous steps.


.. warning::

    Any special configuration or tune setting in your ``postgresql.conf`` will not be reported,
    you should report configuration yourself in ``/etc/postgresql/14/main/postgresql.conf``.
    Then restart your PostgreSQL

    ::

        sudo systemctl restart postgresql



Now, you can update your Geotrek-admin configuration to use the new PostgreSQL server, by changing its default port to the new one.


::

    sudo dpkg-reconfigure geotrek-admin


And change ``POSTGRES_PORT`` to 5433


You can now upgrade your Geotrek-admin, and check that the right database is used.

.. note::

    If you want to use default 5432 port, you should change it in ``/etc/postgresql/14/main/postgresql.conf``,
    restart PostgreSQL service, and change it by reconfiguring Geotrek-admin.

::

        sudo geotrek check_versions --postgresql


If it shows PostgreSQL 14, you can remove the old PostgreSQL version.


::

    sudo apt remove --purge postgresql-10
    sudo apt autoremove


.. _Install pgrouting bionic:

Install PgRouting on Ubuntu Bionic
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

    wget https://raw.githubusercontent.com/GeotrekCE/Geotrek-admin/master/tools/pgrouting_bionic.tar.xz
    tar xavf pgrouting_bionic.tar.xz
    cd pgrouting_bionic
    ./install.sh


::

    sudo -u postgres psql


::

    \c <your geotrek database>
    CREATE EXTENSION pgrouting;
    \q
