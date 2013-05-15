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

* ``var/media/upload/logo-header.png``
* ``var/media/upload/logo-login.png``


Development Data
----------------

::

    bin/django loaddata development-pne


=============
CONFIGURATION
=============


Configuration update
--------------------

After editing ``etc/settings.ini``, refresh the running instance with :

::

    make deploy


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

