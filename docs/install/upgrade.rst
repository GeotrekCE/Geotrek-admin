=======
Upgrade
=======

.. contents::
   :local:
   :depth: 2


From Geotrek-admin >= 2.33
~~~~~~~~~~~~~~~~~~~~~~~~~~

Beforehand you shoud update your system's catalog:

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

To upgrade geotrek-admin to a **specific version**, run:

::

   sudo apt-get install geotrek-admin=<version>

For instance:

::

   sudo apt-get install geotrek-admin=2.97.4.ubuntu18.04

or

::

   sudo apt-get install geotrek-admin=2.98.0.ubuntu20.04

**Note:** all package versions remain available. Even when not listed with ``apt list``.

Once geotrek-admin has been upgraded you may want to prevent unwanted upgrade with the whole distribution, you can run:

::

   sudo apt-mark hold geotrek-admin


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


Ubuntu bionic PostGIS 2.5 upgrade
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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


PostgreSQL
~~~~~~~~~~

Geotrek-admin support PostgreSQL 10+ and PostGIS 2.5+ for now.
In next release, Django 4.2 will drop PostgreSQL < 12 support.
We recommend to upgrade to PostgreSQL 16 and PostGIS 3.4.

You can check your PostgreSQL version with the following command:

::

   sudo geotrek check_versions --postgresql


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


Update PostgreSQL / PostGIS on Ubuntu Bionic
--------------------------------------------

.. warning::

    Ubuntu Bionic is already deprecated. We recommend you to install PostgreSQL on a dedicated server, with a most recent version of Ubuntu.
    If possible, on the same host or datacenter than your Geotrek-admin instance.
    If you can't, you can follow these instructions to upgrade PostgreSQL and PostGIS on Ubuntu Bionic with official PostgreSQL APT archive repository.
    The ultimate version published for Bionic is PostgreSQL 14, supported until November 12, 2026.

::

    sudo rm /etc/apt/sources.list.d/pgdg.list
    sudo apt install curl ca-certificates
    sudo install -d /usr/share/postgresql-common/pgdg
    sudo curl -o /usr/share/postgresql-common/pgdg/apt.postgresql.org.asc --fail https://www.postgresql.org/media/keys/ACCC4CF8.asc
    sudo sh -c 'echo "deb [signed-by=/usr/share/postgresql-common/pgdg/apt.postgresql.org.asc] https://apt-archive.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
    sudo apt update


Then, make a database dump.

::

    sudo -u postgres pg_dump -Fc --no-acl --no-owner -d <your geotrek database name> > /path/to/your/backup.dump


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

    You should report configuration from /etc/postgresql/10/pg_hba.conf to /etc/postgresql/14/pg_hba.conf.
    Then restart your postgresql

    ::

        sudo cp /etc/postgresql/10/pg_hba.conf /etc/postgresql/14/pg_hba.conf
        sudo systemctl restart postgresql


You can now restore your database dump.


::

    pg_restore -p 5433 -U <your geotrek user> -d <your geotrek database> /path/to/your/backup.dump


.. warning::

    Any special configuration or tune setting in your `postgresql.conf` will not be reported,
    you should report configuration yourself in /etc/postgresql/14/postgresql.conf.
    Then restart your postgresql

    ::

        sudo systemctl restart postgresql



Now, you can update your Geotrek-admin configuration to use the new PostgreSQL server, by changing its default port to the new one.


::

    sudo dpkg-reconfigure geotrek-admin


And change ``POSTGRES_PORT`` to 5433


You can now upgrade your Geotrek-admin, and check that the right database is used.

.. note::

    If you want to use default 5432 port, you should change it in `postgresql.conf`,
    restart postgresql service, and change it by reconfiguring Geotrek-admin.

::

        sudo geotrek check_versions --postgresql


If it shows PostgreSQL 14, you can remove the old PostgreSQL version.


::

    sudo apt remove --purge postgresql-10
    sudo apt autoremove
