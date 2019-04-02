============
INSTALLATION
============

These instructions will install *Geotrek* on a dedicated server for production.

Requirements
------------

* Ubuntu Server 18.04 Bionic Beaver (http://releases.ubuntu.com/18.04/)  or
  Ubuntu Server 16.04 Xenial Xerus (http://releases.ubuntu.com/16.04/) or
  Ubuntu Server 14.04 Trusty Tahr (http://releases.ubuntu.com/14.04/)

A first estimation of minimal required system resources are :

* 2 cores
* 4 Go RAM
* 20 Go disk space

For big instances required system resources are :

* 4 cores
* 8 Go RAM or more
* 50 Go disk space or more (20 Go + estimated size of attached files like photos, including elements imported from SIT)


Installation
------------

Once the OS is installed (basic installation, with OpenSSH server), log in with your linux user (not root).
You will also need unzip and wget (``sudo apt-get install unzip wget``).

Choose your folder,
you can choose for exemple :
::

    cd /home/mylinuxuser

Download the latest version of Geotrek-admin with the following commands above 2.21.0 version,
you need to replace X.Y.Z  with the latest stable version number : https://github.com/GeotrekCE/Geotrek-admin/releases) :

::

    wget https://github.com/GeotrekCE/Geotrek-admin-starter/archive/X.Y.Z.zip

Unzip the archive of Geotrek-admin

::

    unzip Geotrek-admin-X.Y.Z.zip

You can rename Geotrek-admin-X.Y.Z folder to Geotrek-admin

Go into Geotrek-admin folder and launch its installation
::
    cd Geotrek-admin


Create Data Base and user
::

    su - postgres
    psql



    CREATE USER your_database_user WITH ENCRYPTED PASSWORD 'your_user_password';
    CREATE DATABASE your_database WITH OWNER your_database_user;
    \c your_database
    CREATE EXTENSION POSTGIS;
    SELECT PostGIS_version(); # Check version.
    \q


___

Modify file .env.dist :
::
    $ cp .env.dist .env
    $ editor .env



    GEOTREK_VERSION=geotrek_version
    POSTGRES_HOST=172.17.0.1
    POSTGRES_USER=your_database_user
    POSTGRES_DB=your_database
    POSTGRES_PASSWORD=your_user_password
    DOMAIN_NAME=your.final.geotrek.domain
    SECRET_KEY=secret-and-unique-secret-and-unique
    GUNICORN_CMD_ARGS=--bind=0.0.0.0:8000 --workers=5 --timeout=600


For the version of geotrek check : https://hub.docker.com/r/geotrekce/admin/tags/

:notes:

    If you leave *172.17.0.1* for POSTGRES_HOST, the postgresql will be locally.

    In order to use a remote server (*recommended*), set the appropriate values
    for the connection.


Edit your custom parameters file
::
    sudo nano ./var/conf/custom.py


Modify at least your :
- SRID => Projection of your project
- SPATIAL_EXTENT => BBOX of the project
- DEFAULT_STRUCTURE_NAME => Name of your structure (ex: geotrek)
- MODELTRANSLATION_LANGUAGES => https://fr.wikipedia.org/wiki/Liste_des_codes_ISO_639-1 (693-1)


Change Working Directory in geotrek.service
::
    WorkingDirectory=/directory_of_your_geotrek


Initialize the project :
::
    docker-compose run web initial.sh


____

Install Service


1. Create a symbolic link between your nginx and /etc/nginx/sites-enabled/
::
     mkdir var/www/geotrek -p

     ln -s /directory_of_your_geotrek/var/media /var/www/geotrek

     ln -s /directory_of_your_geotrek/var/static /var/www/geotrek

     ln -s /directory_of_your_geotrek/nginx.conf /etc/nginx/sites-enabled/geotrek.conf



2. Copy your service in /etc/systemd/system
::
    cp geotrek.service /etc/systemd/system/geotrek.service


3. Enable the system
::
    systemctl enable geotrek.service


Create your first user :
::
     $ docker-compose run --rm web ./manage.py createsuperuser
