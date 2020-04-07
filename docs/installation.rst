============
INSTALLATION
============

Use these instructions to install Geotrek-admin in an easy way on a dedicated Ubuntu Bionic 18.04 LTS server for production.
For another distributions, please use :ref:`the Docker installation method <docker-section>`. It requires more technical skills.
Lastly, for a developer instance, please follow :ref:`the dedicated procedure <development-section>`.


Requirements
------------

A first estimation of minimal required system resources are :

* 2 cores
* 4 Go RAM
* 20 Go disk space

For big instances required system resources are :

* 4 cores
* 8 Go RAM or more
* 50 Go disk space or more (20 Go + estimated size of attached files like photos, including elements imported from SIT)

Software requirements are :

* Ubuntu Bionic 18.04 LTS. Server flavor is recommended but any other flavors work too (desktop…)

An Internet connection with open HTTP and HTTPS destination ports is required.


Information to prepare before installation
------------------------------------------

* The **domain name** to use to access to **Geotrek-admin** web site.
* Rando server name: the **domain name** to use to access to **Geotrek-rando** web site (if appropriate).
* Postgresql **host, port, user, password and DB name** if you use an external DB server.
* The **SRID** of the projection to use to store geometries. The projection must match your geographic area and coordinates must be in meters.
* The list of **languages** into which translation of contents will be made
* The name or acronym of your **organization**


Fresh installation
------------------

Run the following command in a shell prompt on your server:

::

   curl https://packages.geotrek.fr/install.sh | bash

If you don't want to use a local database, you could run the following command instead.
This will prevent the script to install postgresql server locally.
Don't forget to enable postgis extension in your remote database before installation.

::

   curl https://packages.geotrek.fr/install.sh | bash -s - --nodb

Then create the administrator account and connect to the web interface.

::

   sudo geotrek createsuperuser

If you are not confident with the install.sh script, or if you are having troubles, you can do the same operations by hand:

1. Add ``deb https://packages.geotrek.fr/ubuntu bionic main`` to apt sources list.
2. Add https://packages.geotrek.fr/geotrek.gpg.key to apt keyring.
3. Run ``apt-get update``
4. If you want to use a local database, install postgis package (before installing geotrek-admin, not at the same time).
   If not, you must create database and enable postgis extension before.
5. Install the geotrek-admin package.


Upgrade from Geotrek-admin >= 2.33
----------------------------------

To upgrade the whole server, includind, geotrek-admin, run:

::

   apt-get update
   apt-get upgrade

To prevent upgrading geotrek-admin with the whole distribution, you can run:

::

   sudo apt-mark hold geotrek-admin

To upgrade only Geotrek-admin and its dependencies, run:

::

   apt-get install geotrek-admin


Upgrade from Geotrek-admin <= 2.32
----------------------------------

Go inside your existing Geotrek-admin installation directory. Then run:

::

   curl https://packages.geotrek.fr/migrate.sh | bash


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

Note: postgresql and database will not be removed by these commands. If need be, remove them manually.
