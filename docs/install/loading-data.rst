.. _loading-data-section:

============
Loading data
============


Prerequisites for your data
---------------------------

Layers
~~~~~~

* WMTS protocol
* WebMercator Projection

Core
~~~~

* Only LineString geometries
* Simple geometries
* Not overlapping

If possible:

* Connex graph
* Name column
* Data source

Formats: Shapefile or pure SQL dump (CREATE TABLE + INSERT)


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

In `QGIS <http://docs.qgis.org/latest/en/docs/training_manual/processing/cutting_merging.html>`_,
you can visualize your DEM, or merge several tiles together (in *Raster* > *Misc* > *Merge*).

Generate a GeoTIFF, and upload both files (``.tif`` + ``.tfw``) on the server.
And use the Geotrek-admin command to load it into PostGIS :

::

    sudo geotrek loaddem <PATH>/dem.tif


.. note ::

    This command makes use of *GDAL* and ``raster2pgsql`` internally. It
    therefore supports all GDAL raster input formats. You can list these formats
    with the command ``raster2pgsql -G``.
    
.. note ::

    If you only have a ``.tif`` file, you can generate the ``.tfw`` file with the command ``gdal_translate -co "TFW=YES" in.tif out.tif``. 
	It will generate a new ``.tif`` file with its ``.tfw`` metadata file.
