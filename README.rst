**Geotrek**, a *Natural Park* Manager

=====
SETUP
=====

Requirements
------------

* Ubuntu Server 12.04 Precise Pangolin (http://releases.ubuntu.com/12.04/)


A first estimation on system resources is :

* 1 Go RAM
* 10 Go disk space


Installation
------------

Once the OS is installed (basic installation, with OpenSSH server), copy and extract the source archive.

Go into the extracted directory, just follow the installation process :

::

    ./install.sh

You will mainly be prompt for editing the base configuration file (``settings.ini``),
using *Vim* (Finish with 'Esc' then ':wq' to save and quit).

To make sure the application runs well after a reboot, try now : reboot. And
access the ``http://yourserver/``.

See information below for configuration and loading initial demonstration data.


Software update
---------------

Keep previous versions in separate folders (**recommended**).

First, copy your old configuration and uploaded files to your new folder.

::

    # Configuration files
    mkdir -p etc/
    cp ../previous-version/etc/settings.ini etc/
    # Uploaded files
    mkdir -p var/
    cp -R ../previous-version/var/tiles var/tiles
    cp -R ../previous-version/var/media var/media

Shutdown previous running version, and run install :

::

    # Shutdown previous version
    ../previous-version/bin/supervisorctl stop all
    sudo service supervisor stop

    # Re-run install
    ./install.sh

    # Reload configuration
    sudo service supervisor restart


Or instead, if you prefer, you can overwrite the source code and run ``./install.sh``.


Tips and Tricks
---------------

* Use symlinks for uploaded files and cached tiles to avoid duplicating them on disk:

::

    mv var/tiles ~/tiles
    ln -s ~/tiles `pwd`/var/tiles

    mv var/media ~/media
    ln -s ~/media `pwd`/var/media


* Speed-up upgrades by caching downloads :

::

    mkdir ~/downloads
    mkdir  ~/.buildout

Create ``/home/sentiers/.buildout/default.cfg`` with ::

    [buildout]
    download-cache = /home/sentiers/downloads


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


===============
TROUBLESHOOTING
===============

Installation script hangs on syncdb --migrate
---------------------------------------------

This command is in charge of changing the database schema [1].

Make sure you close every *pgADMIN* session on the database while upgrading.

[1] http://south.aeracode.org/ticket/209


No paths in list, where table contains records
----------------------------------------------

Check that the projection of your data is correct. Check that the extent of the map covers your data.

Check the value of the ``spatial_extent_wgs84``` setting.


No background tiles
-------------------

Check the values of your WMS settings (server name should end with ``?``, layers names should exist on server).

Check the values in the generated TileCache configuration in ``etc/tilecache.cfg``.


Error at loading DEM
--------------------

Check that your extent (``spatial_extent``) is completely contained in your DEM.


===========
DEVELOPMENT
===========

For code contributors only : in order to run a development instance :

::

    ./install.sh --dev

Start local instance :

::

    make serve


Run unit tests :

::

    make tests

For PDF conversion server, run an instance in a separate terminal :

::

    bin/pserve lib/src/convertit/development.ini

=======
AUTHORS
=======

    * Gilles Bassière
    * Sylvain Beorchia
    * Mathieu Leplatre
    * Anaïs Peyrucq
    * Satya Azemar
    * Simon Thépot

|makinacom|_

.. |makinacom| image:: http://depot.makina-corpus.org/public/logo.gif
.. _makinacom:  http://www.makina-corpus.com


=======
LICENSE
=======

    * BSD
    * (c) Parc National des Écrins - Parc National du Mercantour - Parco delle Alpi Marittime - Makina Corpus
