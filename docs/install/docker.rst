.. _docker-section:

======
Docker
======

.. contents::
   :local:
   :depth: 2

Docker is an alternative installation method, recommended for experts only.
It allows to install several instances of Geotrek-admin on the same serveur,
and to install it on other distributions than Ubuntu Linux 18.04.


Installation
------------

1. Install Docker and Docker Compose, either from your distribution or from upstream packages
   (cf. https://docs.docker.com/install/)
2. Download the code from https://github.com/GeotrekCE/Geotrek-admin/releases
   or checkout it with git from https://github.com/GeotrekCE/Geotrek-admin/
3. Unzip the tarball
4. Copy docker/install folder where you want
4. Edit `docker-compose.yml` to feed your needs if necessary
5. Copy `.env.dist` to `.env` and edit to feed your needs if necessary
6. Create user and database, enable PostGIS extension
7. Run `docker-compose run --rm web update.sh`
8. Run `docker-compose up`
9. Install NGINX (or equivalent) and add a configuration file (taking inspiration from `nginx.conf.in`)

Management commands
-------------------

Replace ``sudo geotrek …`` commands by ``cd <install directory>; docker-compose run --rm web ./manage.py …``

To load minimal data and create an application superuser, run :

::

   docker-compose run --rm web load_data.sh
   docker-compose run --rm web ./manage.py createsuperuser
