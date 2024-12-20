.. _minimal-initial-data:

======================
Minimal initial data
======================

.. IMPORTANT::
   These data are the minimal initial data required to have a functional Geotrek-admin after completing the :ref:`installation <installation>`.

Basemap layers
===============

* WMTS protocol (OSM, IGN...)
* WebMercator Projection

Core paths
===========

* Only LineString geometries
* Simple geometries
* Not overlapping

If possible:

* Connex graph
* Name column
* Data source

Formats: Shapefile or pure SQL dump (CREATE TABLE + INSERT)

Land
=====

* Cities polygons (Shapefile or SQL, simple and valid Multi-Polygons)
* Districts (Shapefile ou SQL, simple and valid Multi-Polygons)
* Restricted Areas (Shapefile ou SQL, simple and valid Multi-Polygons)

Extras
=======

* Languages list
* Structures list (and default one)

