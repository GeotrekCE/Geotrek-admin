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
is available at *http://server/tools/extents/*.

:notes:

    Administrator privileges are required.


Custom spatial reference
------------------------

*Geotrek* comes with a few projection systems included (*EPSG:2154*, *EPSG:32600*,
*EPSG:32620*, *EPSG:32632*)

In order to use a specific projection system :

* Make sure the SRID is present in the ``spatial_ref_sys`` table. See PostGIS
  documentation to add new ones
* Download the JavaScript *proj4js* definition from `http://spatialreference.org`_
  and save it to `Geotrek/static/proj4js/<SRID>.js`

Using the command-line :

::

    curl "http://spatialreference.org/ref/epsg/<SRID>/proj4js/" > Geotrek/static/proj4js/<SRID>.js


:note:

    *Geotrek* won't run if the spatial reference has not a metric unit.

It's possible to store your data using a specific SRID, and use a classic
Google Maps projection (3857) in the Web interface (useful for *WMTS* or *OpenStreetMap* layers).
See :ref:`advanced configuration <advanced-configuration-section>`...


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
recipients emails (``mailadmins``, ``mailmanagers``) as well as server
parameters (``host``, ``user``, ``password``, ...)

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

.. code-block:: bash

    sudo apt-get update
    sudo apt-get dist-upgrade


Application backup
------------------

Give postgresql the right to write files in application folder :

.. code-block:: bash

    sudo adduser postgres `whoami`

Database

.. code-block:: bash

    sudo su postgres
    pg_dump -Fc geotrekdb > /home/sentiers/`date +%Y%m%d%H%M`-database.backup
    exit

Media files

.. code-block:: bash

    cd Geotrek-vX.Y.Z/
    tar -zcvf /home/sentiers/`date +%Y%m%d%H%M`-media.tar.gz var/media/


Configuration

.. code-block:: bash

    # Folder Geotrek-vX.Y.Z/
    tar -zcvf /home/sentiers/`date +%Y%m%d%H%M`-conf.tar.gz etc/ geotrek/settings/custom.py



Application restore
-------------------

Create empty database :

.. code-block:: bash

    sudo su postgres

    psql -c "CREATE DATABASE ${dbname} ENCODING 'UTF8' TEMPLATE template0;"
    psql -d geotrekdb -c "CREATE EXTENSION postgis;"


Restore backup :

.. code-block:: bash

    pg_restore -d geotrekdb 20140610-geotrekdb.backup
    exit


Extract media and configuration files :

.. code-block:: bash

    cd Geotrek-vX.Y.Z/
    tar -zxvf 20140610-media.tar.gz
    tar -zxvf 20140610-conf.tar.gz

Re-run ``./install.sh``.


PostgreSQL optimization
-----------------------

* Increase ``work_mem`` according to your RAM (e.g. 30%)

* `Log long queries <http://wiki.postgresql.org/wiki/Logging_Difficult_Queries>`_

* Use `pg activity <https://github.com/julmon/pg_activity#readme>`_ for monitoring


Access your database securely on your local machine (QGis)
----------------------------------------------------------

Instead of opening your database to the world (by opening the port 5432 for
example), you can use `SSH tunnels <http://www.postgresql.org/docs/9.3/static/ssh-tunnels.html>`_.
