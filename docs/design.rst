======
DESIGN
======

Architecture
------------

.. image :: images/architecture-1.0.jpg
    :width: 50%

* **Geotrek**, the web application
* **TileCache**, tile and cache remote WMS servers
* **Convertit**, a Web API to convert document and image formats (*.odt to .doc*, *.svg to .png*)
* **Screamshotter**, a Web API to perform Web pages screenshots (*map image exports*).


Main components
---------------

The whole project is built on top of *mapentity*.


A generic application in charge of:

* Menus and models registry
* List/Detail/Create/Update/Delete views
* Filtering
* Map images exports
* File attachment
* Document export
* Shapefile/GPX/CSV serializers

For a Django model, we use the registry to activate all views and menus :

.. image :: images/mapentity.jpg
    :width: 50%

Business specific notions are implemented in Geotrek respective applications:

* **common**: shared concepts between all applications (*Organism*, *utils*, ...)
* **authent**: groups, user, profile and structure notions. Optional external authent backend.
* **core**: elevation, paths, snapping, spatial referencing (topologies)
* **land**: static cities/districts/restricted areas layers, physical types, competence,
  signage and work management
* **infrastructure**: buildings, signages, equipements
* **maintenance**: interventions (on paths or on infrastructures) and projects
* **trekking**: POIs and treks


Django conventions twists
-------------------------

We have a couple of Django conventions infringements:

* Buildout: (see *DEPLOYMENT* section)
* SQL triggers everywhere: since Geotrek database is to become the central storage
  component of all park organisation data, it has to behave consistently whether data is
  modified through the Web application or raw access tools (pgadmin, QGIS).
  (For example, insertion & update timestamps, geometry computation or DEM wrapping.)
* Safe delete: update field ``deleted = True`` instead of performing actual delete in table.
  Requires every querysets to be filtered on deleted. (**TODO**: use dango-safedelete, `issue 813 <https://github.com/makinacorpus/Geotrek/issues/813>`_)


Main roles of PostgreSQL triggers
---------------------------------

Automatic computation of fields :

* Date insert/update
* Geometry computation of linear referencing (topologies)
* DEM elevation wrapping (3D length, slope, etc.)

Topological path network :

* Split paths at intersection
* Snap paths extremities


Why buildout ?
--------------

* Multiple sub-projects under development (*mr.developer*)
* GDAL installation (*include-dirs*)
* Unique and simple file for user settings input (*etc/settings.ini*)
* Simple provisionning (*configuration templating*)
* Python dependencies versions consistency
* Multiple sets of dependencies (*dev, tests, prod*)


install.sh script
-----------------

* No need for multiple OS support
* Can be run just from the project archive
* Install system dependencies
* Single tenant on dedicated server
* Idem-potent, used for both installation and upgrade


etc/settings.ini
----------------

* Centralize configuration values (for both Django and system configuration files)
* Easy syntax
* Default and overridable values (*conf/settings-default.ini*)

Regarding Django settings organisation:

* All application settings have a default (working) value in *settings/base.py*.
* The mechanizm that uses *etc/settings.ini* takes place in *settings/default.py* **only**.
  This means that other settings management can be derived from *base.py*.
* Production settings (*settings/prod.py*) contains tweaks that are relevant in production only.
