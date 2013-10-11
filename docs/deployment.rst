=============
CONFIGURATION
=============


Configuration update
--------------------

After editing ``etc/settings.ini``, refresh the running instance with :

::

    make deploy


There a few cases where running ``install.sh`` would be necessary. If you
change the ``rooturl`` or other parameters that affect *nginx* site configuration.


Spatial extents
---------------

In order to check your configuration of spatial extents, a small tool
is available at *http://server/tools/extent/*.

:notes:

    Administrator privileges are required.


External authent
----------------

You can authenticate user against a remote database table or view.

To enable this feature, fill *authent_dbname* and other fields in ``etc/settings.ini``.

Expected columns in table/view are :

* username : string (*unique*)
* first_name : string
* last_name : string
* password : string (simple md5 encoded, or full hashed and salted password)
* email : string
* level : integer (1: readonly, 2: redactor, 3: path manager, 4: trekking manager, 6: administrator)
* structure : string
* lang : string (language code)


:notes:

    User management will be disabled from Administration backoffice.

    In order to disable remote login, just remove *authent_dbname* value in settings
    file, and update instance (see paragraph above).

    Geotrek can support many types of users authentication (LDAP, oauth, ...), contact-us
    for more details.


Custom setting file
-------------------

Geotrek configuration is currently restricted to values present in ``etc/settings.ini``.

However, it is still possible to write a custom Django setting file.

* Create your a file in *geotrek/settings/custom.py* with the following content ::

    from .prod import *

    # My custom value
    HIDDEN_OPTION = 3.14

* Add this ``etc/settings.ini`` to specify the newly created setting ::

    [django]
    settings = settings.custom

* As for any change in settings, re-run ``make deploy``.


============
LOADING DATA
============

Prerequisites
-------------

Layers
~~~~~~

* WMS (scan + ortho)
* Projection
* Bounding box in native projection

Core
~~~~

* Only LineString geometries
* Simple geometries
* Not overlapping

If possible :

* Connex graph
* Name column
* Data source

Formats: Shapefile or pure SQL dump SQL (CREATE TABLE + INSERT)


Land
~~~~

* Cities polygons (Shapefile or SQL, simple and valid Multi-Polygons)
* Districts (Shapefile ou SQL, simple and valid Multi-Polygons)
* Restricted Areas (Shapefile ou SQL, simple and valid Multi-Polygons)

Extras
~~~~~~

* Languages list
* Structures list (and default one)


Load MNT raster
---------------

::

    bin/django loaddem <PATH>/w001001.adf


:note:

    This command makes use of *GDAL* and ``raster2pgsql`` internally. It
    therefore supports all GDAL raster input formats. You can list these formats
    with the command ``raster2pgsql -G``.


Initial Data
------------

Load basic data :

::

    make load_data


If you do not load data, you'll have to at least create a super user :

::

    bin/django createsuperuser --username=admin --email=admin@corp.com

or change its password :

::

    bin/django changepassword --username admin <password>

You might also need to deploy logo images in the following places :

* ``var/media/upload/favicon.png``
* ``var/media/upload/logo-login.png``



===========
MAINTENANCE
===========


Operating system updates
------------------------

::

    sudo apt-get update
    sudo apt-get dist-upgrade


Application backup
------------------

Database

::

    sudo su postgres
    pg_dump -Fc geotrekdb > `date +%Y%m%d%H%M`-database.backup

Media files

::

    tar -zcvf `date +%Y%m%d%H%M`-media.tar.gz var/media/


PostgreSQL optimization
-----------------------

* Increase ``work_mem`` according to your RAM (e.g. 30%)

* `Log long queries <http://wiki.postgresql.org/wiki/Logging_Difficult_Queries>`_

* Use `pg activity <https://github.com/julmon/pg_activity#readme>`_ for monitoring
