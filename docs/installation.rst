============
INSTALLATION
============

These instructions will install *Geotrek* on a dedicated server for production.
For a developer instance, please follow  :ref:`the dedicated procedure <development-section>`.

Requirements
------------

A first estimation of minimal required system resources are :

2 cores
4 Go RAM
20 Go disk space
For big instances required system resources are :

4 cores
8 Go RAM or more
50 Go disk space or more (20 Go + estimated size of attached files like photos, including elements imported from SIT)


Installation
------------
**INSTALL DOCKER AND DOCKER-COMPOSE**

Check your linux distribution :

::

    sudo cat /etc/issue

Find the most adequate docker install in :
https://docs.docker.com/install/
Example ubuntu :
https://docs.docker.com/install/linux/docker-ce/ubuntu/

And docker-compose :
https://docs.docker.com/compose/install/#install-compose



Once the OS is installed (basic installation), log in with an other user (not root).

   You should not launch docker with root.


**CREATE THE FOLDER OF YOUR INSTANCE**

::

    mkdir /path/of/your/instance/geotrek
    cd  /path/of/your/instance/geotrek

*Later in this install /path/of/your/instance/geotrek is /srv/geotrek*

**FIX RIGHTS**

Fix rights and log in with your user for all operations

::

    chown -R geotrek:geotrek /srv/geotrek
    su - geotrek

**GET YOUR DOCKER-COMPOSE**

::

    wget https://raw.githubusercontent.com/GeotrekCE/Geotrek-admin/docker-integration/install/docker-compose.yml


**CREATE ENVIRONMENT OF INSTALL**

In your instance folder create a ``.env`` file

In this example : the server is inside a container of docker. You may want to use a remote database server (separate) or a locale one.
Change POSTGRES_HOST and every information about POSTGRES and PGPORT
::

    GEOTREK_VERSION=<VERSION OF GEOTREK>  # Check changelog
    POSTGRES_HOST=postgres
    POSTGRES_USER=<your_personnal_database_user>
    POSTGRES_DB=<your_personnal_database_user>
    POSTGRES_PASSWORD=<your_personnal_database_password>
    DOMAIN_NAME=<your.geotrek.com>
    SECRET_KEY=<your_personnal_secret_key>
    PGPORT=5432
    REDIS_HOST=redis
    REDIS_PORT=6379
    REDIS_DB=0
    CONVERSION_HOST=convertit
    CONVERSION_PORT=6543
    CAPTURE_HOST=screamshotter
    CAPTURE_PORT=8000

:notes:
    In order to use a remote database server (*recommended*), set the appropriate values
    for the connection.
    The connection must be operational (it will be tested during install).
    *make sure postgresql > 9.3 and postgis > 2.1*
    Add these environment variables :

        POSTGRES_HOST=<your_host_or_ip>
        PGPORT=<your_port>

    *and comment postgresql section in docker-compose.yml*

        volumes:
            postgres:


**CREATE THE VAR FOLDER**

::

    mkdir -p var
    docker-compose run web /bin/sh -c exit

**EDIT YOUR CUSTOM.py FILE**

The custom.py file is in ``var/conf``
Set at least MODELTRANSLATION_LANGUAGES / SRID / SPATIAL_EXTENT / DEFAULT_STRUCTURE_NAME

::

    cd ./var/conf
    sudo editor custom.py

     _________________________________________________________

        MODELTRANSLATION_LANGUAGES = ('en', 'fr', 'it', 'es')

        SRID = 2154

        SPATIAL_EXTENT = (105000, 6150000, 1100000, 7150000)

        DEFAULT_STRUCTURE_NAME = 'GEOTEAM'


**INITIATE DATABASE**

::

    docker-compose run postgres -d

**INITIATE REQUIRED DATAS** *WARNING Only from scratch*

::
    docker-compose run web initial.sh


**CREATE USER**

::

    docker-compose run web ./manage.py createsuperuser


**INSTALL GEOTREK AS SERVICE**

Use this example : ``install/geotrek.service``

::

    wget https://raw.githubusercontent.com/GeotrekCE/Geotrek-admin/docker-integration/install/geotrek.service

Modify line :

::

    WorkingDirectory=<absolute path of your instance>


Enable it

::

    sudo cp geotrek.service /etc/systemd/system/geotrek.service
    sudo systemctl enable geotrek

**USE SSL**

Put your certificate and key in this folder
Uncomment and edit docker-compose.yml nginx section
Edit custom.py (uncomment SESSION_COOKIE_SECURE = True, CSRF_COOKIE_SECURE = True)
Edit your geotrek_nginx.conf with mounted path of your files


**RUN, STOP, UPDATE GEOTREK**

For run, stop or after any update your geotrek instance do this command.

::

    sudo systemctl start geotrek
    sudo systemctl stop geotrek

