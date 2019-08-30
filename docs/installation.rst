============
INSTALLATION
============

These instructions will install *Geotrek* on a dedicated server for production.
For a developer instance, please follow  :ref:`the dedicated procedure <development-section>`.


Installation
------------
**INSTALL DOCKER AND DOCKER-COMPOSE**

Check your linux distribution :

::

    sudo cat /etc/issue

Find the most adequate docker install in :
https://docs.docker.com/install/linux/docker-ce/ubuntu/

And docker-compose :
https://docs.docker.com/compose/install/#install-compose



Once the OS is installed (basic installation), log in with an other user.

   You should not launch docker with root.


**CREATE A DEDICATED USER**

Do the following 3 commands or use your user and do the last command for your user.

::

    useradd geotrek
    adduser geotrek sudo

    adduser geotrek docker



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
    In order to use a remote server (*recommended*), set the appropriate values
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

