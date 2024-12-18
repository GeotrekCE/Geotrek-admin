================
Load MNT raster
================

.. contents::
   :local:
   :depth: 2

In `QGIS <http://docs.qgis.org/latest/en/docs/training_manual/processing/cutting_merging.html>`_,
you can visualize your DEM, or merge several tiles together (in *Raster* > *Misc* > *Merge*).

Generate a GeoTIFF, and upload both files (``.tif`` + ``.tfw``) on the server.
And use the Geotrek-admin command to load it into PostGIS :

::

    sudo geotrek loaddem <PATH>/dem.tif

.. note::

    - This command makes use of *GDAL* and ``raster2pgsql`` internally. It therefore supports all GDAL raster input formats. You can list these formats with the command ``raster2pgsql -G``.
    - The elevation data of DEM must be integer values. If the elevation data are floating numbers, you can convert them in integer values with the Raster calculator processing of `SAGA in QGis <https://docs.qgis.org/3.34/en/docs/user_manual/processing/3rdParty.html#saga>`_ (Processing > Toolbox > SAGA > Raster calculus > Raster calculator) with formula parameter set to ``int(a)``.
    - If you only have a ``.tif`` file, you can generate the ``.tfw`` file with the command ``gdal_translate -co "TFW=YES" in.tif out.tif``. It will generate a new ``.tif`` file with its ``.tfw`` metadata file.
    - If you want to  update the altimetry of the topologies you need to use the option ``--update-altimery``
