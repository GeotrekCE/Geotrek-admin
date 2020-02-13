============
INSTALLATION
============

These instructions will install *Geotrek* on a dedicated server for production.
For a developer instance, please follow  :ref:`the dedicated procedure <development-section>`.


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


Method 1: Bash script (recommended)
-----------------------------------

This method works only on Ubuntu Bionic 18.04 LTS.

1. Run `curl https://packages.geotrek.fr/install.sh | bash` on your server.

If you don't want to use a local database, you could run
`curl https://packages.geotrek.fr/install.sh | bash -s - --nodb` instead.
This will prevent the script to install postgresql server locally.
Don't forget to enable postgis extension in your remote database before Geotrek-admin installation.


Method 2: Manual installation
-----------------------------

Same as above, by hand.

1. Add `deb https://packages.geotrek.fr/ubuntu bionic main` to apt sources list.
1. Add https://packages.geotrek.fr/geotrek.gpg.key to apt keyring.
1. Run `apt-get update`
1. If you want to use a local database, install postgis package (before installing geotrek-admin, not at the same time).
   If not, you must create database and enable postgis extension before.
1. Install geotrek-admin package.


Method 2: Docker
----------------

See :ref:`docker installation <docker-section>`...
