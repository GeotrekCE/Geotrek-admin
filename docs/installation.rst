============
INSTALLATION
============

Use these instructions to install *Geotrek* in an easy way on a dedicated Ubuntu Bionic 18.04 LTS server for production.
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

* Ubuntu Bionic 18.04 LTS. Serve flavor is recommended but any other flavor works too (desktop…)

An Internet connection with open HTTP and HTTPS destination ports is required.


Information to prepare before installation
------------------------------------------

* Server name: the domain name to use to access to Geotrek-admin web site.
* Rando server name: the domain name to use to access to Geotrek-rando web site (if appropriate).
* Postgresql host, port, user, password and DB name if you use an external DB server.
* The SRID of the projection to use to store geometries. The projection must match your geographic area and coordinates must be in meters.
* The list of languages into which translation of contents will be made
* The name or acronym of your organization


Fresh installation
------------------

Run `curl https://packages.geotrek.fr/install.sh | bash` in a shell prompt on your server.

If you don't want to use a local database, you could run
`curl https://packages.geotrek.fr/install.sh | bash -s - --nodb` instead.
This will prevent the script to install postgresql server locally.
Don't forget to enable postgis extension in your remote database before installation.

Then create the administrator account with `sudo geotrek createsuperuser` and connect to the web interface.

If you are not confident with the install.sh script, or if you are having troubles, you can do the same operations by hand:

1. Add `deb https://packages.geotrek.fr/ubuntu bionic main` to apt sources list.
1. Add https://packages.geotrek.fr/geotrek.gpg.key to apt keyring.
1. Run `apt-get update`
1. If you want to use a local database, install postgis package (before installing geotrek-admin, not at the same time).
   If not, you must create database and enable postgis extension before.
1. Install the geotrek-admin package.


Upgrade from Geotrek-admin >= 2.33
----------------------------------

Run `apt-get update`, then `apt-get upgrade` to upgrade the whole server
or `apt-get install geotrek-admin` to upgrade only Geotrek-admin and its dependencies.


Upgrade from Geotrek-admin <= 2.32
----------------------------------

Go inside your existing Geotrek-admin installation directory.
Then run `curl https://packages.geotrek.fr/migrate.sh | bash` .


Uninstallation
--------------

Run `apt-get remove geotrek-admin`. Media files will be left in `/opt/geotrek-admin/var` directory.
Run `apt-get purge geotrek-admin` to remove them.

To remove dependencies (convertit, screamshooter…), run `apt-get autoremove`.
