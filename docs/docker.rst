.. _docker-section:

======
DOCKER
======

Docker is an alternative installation method, recommended for experts only.
It allows to install several instances of Geotrek-admin on the same serveur,
and to install it on other distributions than Ubuntu Linux 18.04.


Installation
------------

1. Install docker and docker-compose, either from your distribution or from upstream packages
(cf. https://docs.docker.com/install/)
1. Download the code from https://github.com/GeotrekCE/Geotrek-admin/releases
   or checkout it with git from https://github.com/GeotrekCE/Geotrek-admin/
1. Unzip the tarball
1. Copy docker-compose-prod.yml to docker-compose.yml and edit to feed your needs if necessary
1. Copy .env-prod.dist to .env and edit to feed your needs if necessary
1. Create user and database, enable postgis extension
1. Run docker-compose run --rm web update.sh
1. Run docker-compose up


Management commands
-------------------

Replace `sudo geotrek …` command by `cd <install directory>; docker-compose run --rm ./manage.py …`
