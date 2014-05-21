=============
CONFIGURATION
=============


Configuration update
--------------------

After editing ``etc/settings.ini``, refresh the running instance with :

::

    make env_standalone deploy


There a few cases where running ``install.sh`` would be necessary. If you
change the ``rooturl`` or other parameters that affect *nginx* site configuration.


Spatial extents
---------------

In order to check your configuration of spatial extents, a small tool
is available at *http://server/tools/extent/*.

:notes:

    Administrator privileges are required.


Users management
----------------

Geotrek relies on Django authentication and permissions system : Users belong to
groups and permissions can be assigned at user or group-level.

The whole configuration of user, groups and permissions is available in the *AdminSite*,
if you did not enable *External authent* (see below).

By default four groups are created :

* Readers
* Path managers
* Trek managers
* Editor

Once the application is installed, it is possible to modify the default permissions
of these existing groups, create new ones etc...

If you want to allow the users to access the *AdminSite*, give them the *staff*
status using the dedicated checkbox.


Email settings
--------------

Geotrek will send emails :

* to administrators when internal errors occur
* to managers when a feedback report is created

Email configuration takes place in ``etc/settings.ini``, where you control
recipients emails as well as server parameters (host, user, password, ...)

You can test you configuration with the following command. A fake email will
be sent to the managers :

::

    bin/django test_managers_emails


Advanced Configuration
----------------------

See :ref:`advanced configuration <advanced-configuration-section>`...


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
