.. _minimal-initial-data:

======================
Minimal initial data
======================

.. IMPORTANT::
   These data are the minimal initial data required to have a functional Geotrek-admin after completing the :ref:`installation <installation>`.

.. _altimetry-dem-source-list:

Altimetry (DEM)
===============

.. abstract:: Keywords

   ``DEM``, ``MNT``, ``raster``, ``QGIS``

**Data sources recommandations**

.. list-table:: Altimetric Data
   :widths: 20 20 20 20 20
   :header-rows: 1

   * - **Name**
     - **Provider**
     - **Coverage**
     - **Resolution**
     - **Format**
   * - `BD Alti <https://geoservices.ign.fr/bdalti>`_
     - IGN
     - Departmental
     - 25 m
     - ``.asc``
   * - `RGE Alti <https://geoservices.ign.fr/rgealti#telechargement5m>`_
     - IGN
     - Departmental
     - 1 m or 5 m
     - ``.asc``

.. warning::

    - We recommend not importing a DEM with too precise resolution for performance reasons. For example, the BD Alti DEM with a 25m resolution is perfect to cover a department.
    - If you downloaded the BD Alti or RGE Alti, you will need to convert the ``.asc`` DEM to ``.tif`` format (e.g. with QGIS) before uploading it on the server.

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

Load DEM
----------

Refer to :ref:`this section <import-dem-altimetry>` to learn how to load DEM with the ``loaddem`` command.

Paths
=======

.. abstract:: Keywords

   ``command line``, ``import en ligne de commande``, ``QGIS``


.. ns-only::

    ..


.. important::
    With :ref:`dynamic segmentation <configuration-dynamic-segmentation>`, importing paths is very risky if paths are already present in the same area in Geotrek,
    it is only safe for an area where no path is already created.

    Indeed, if you import paths where there are existing paths, treks, POIs or trails linked topology might be impacted.

Step 1: Prepare the paths to import
-----------------------------------

By exporting paths from OpenStreetMap
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can use the ``osm-paths`` tool to download OSM paths data via the overpass API. This tool converts paths into linestrings and exports them to GeoJSON.

For more information, refer to the `osm-paths documentation <https://github.com/makinacorpus/osm-paths>`_

By using your own paths
~~~~~~~~~~~~~~~~~~~~~~~

Requirements
""""""""""""

Before importing paths layer, it is important to prepare them. Here are the requirements:

- valid geometry
- simple geometry (no intersection)
- all intersections must cut the paths
- not double or covering others

Cleaning your paths
"""""""""""""""""""

We use QGis to clean a path layer, with plugin Grass.
Here are the operations:

1. Check the SRID (must be the same as in Geotrek)

2. Use the **Geometric tools**:

   1. Go to `Vectors → Geometric tools → "Collect geometries"`.
   2. Then go to `Vectors → Geometric tools → "Group"`.

3. Clean geometries:

   1. Search for `v_clean` in the *Processing toolbox*.
   2. Select the following options in the cleaning tool:

      - `break`
      - `snap`
      - `duplicate` (or `rmdup`)
      - `rmline`
      - `rmdangle`
      - `chdangle`
      - `bpol`
      - `prune`
   3. In **threshold**, enter `2,2,2,2,2,2,2,2` (2 meters for each option).

4. Delete duplicate geometries:

   1. Search for `duplicate` in the *Processing toolbox*.

5. Regroup lines:

   1. Search for `v.build.polyline` in the *Processing toolbox*.
   2. Select `first` in *Category number mode*.

Step 2: Import the paths into your instance
-------------------------------------------

There are two ways to import paths:

- importing a file via the command line by using the ``loadpaths`` command. Refer to :ref:`this section <import-paths>` to learn how to use it
- `using QGis by following this blog post <https://makina-corpus.com/sig-webmapping/importer-une-couche-de-troncons-dans-geotrek>`_.

Step 3: Pre-generate the path graph
-----------------------------------

After importing a large quantity of paths, it is recommended to pre-generate the paths graph needed for the routing.

This action is not mandatory, but will reduce the time needed for the first routing following the import.

To pre-generate the graph, use the ``generate_pgr_network_topology`` command. Refer to :ref:`this section <generate-pgrouting-network-topology>` to learn about this command.


Areas
=======

.. _cities-source-list:

Cities
-------

**Data sources recommandations**

.. list-table:: Administrative Boundaries Data
   :widths: 20 15 20 15 15 15
   :header-rows: 1

   * - **Name**
     - **Provider**
     - **Coverage**
     - **Scale**
     - **Format**
     - **Update Frequency**
   * - `Admin Express <https://geoservices.ign.fr/adminexpress#telechargement>`_ (COMMUNE)
     - IGN
     - Metropolitan France, Overseas Territories
     - Municipality
     - Geopackage, Shapefile
     - Annually
   * - `Administrative Boundaries <https://github.com/datagouv/decoupage-administratif#via-des-urls>`_ ➡ `Communes <https://unpkg.com/@etalab/decoupage-administratif/data/communes.json>`_
     - Etalab
     - Metropolitan France, Overseas Territories
     - Municipality
     - GeoJSON
     - Annually

.. seealso::

	Refer to :ref:`this section <import-cities>` to learn more about loading cities in your Geotrek-admin.

.. _districts-source-list:

Districts
----------

**Data sources recommandations**

.. list-table:: Administrative Boundaries Data (EPCI)
   :widths: 20 15 20 15 15 15
   :header-rows: 1

   * - **Name**
     - **Provider**
     - **Coverage**
     - **Scale**
     - **Format**
     - **Update Frequency**
   * - `Admin Express <https://geoservices.ign.fr/adminexpress#telechargement>`_ (EPCI)
     - IGN
     - Metropolitan France, Overseas Territories
     - EPCI
     - Geopackage, Shapefile
     - Annually
   * - `Administrative Boundaries <https://github.com/datagouv/decoupage-administratif#via-des-urls>`_ ➡ `EPCI <https://unpkg.com/@etalab/decoupage-administratif/data/epci.json>`_
     - Etalab
     - Metropolitan France, Overseas Territories
     - EPCI
     - GeoJSON
     - Annually

Districts are not necessarily administrative boundaries. They can be intercommunalities, departments, parks, or natural regions. The advantage of importing them as Districts is that you will be able to filter them in Geotrek-rando, which will not be possible with Restricted areas.

.. seealso::

	Refer to :ref:`this section <import-districts>` to learn more about loading districts in your Geotrek-admin.

.. _restrictedareas-source-list:

Restricted areas
-----------------

**Data sources recommandations**

.. list-table:: Protected Areas Data
   :widths: 20 15 20 15 15
   :header-rows: 1

   * - **Name**
     - **Provider**
     - **Coverage**
     - **Format**
     - **Update Frequency**
   * - `Natura 2000 <https://inpn.mnhn.fr/telechargement/cartes-et-information-geographique/nat/natura>`_
     - INPN
     - Metropolitan France, Overseas Territories
     - Shapefile
     - Annually
   * - `ZNIEFF1 <https://inpn.mnhn.fr/telechargement/cartes-et-information-geographique/inv/znieff1>`_
     - INPN
     - Metropolitan France, Overseas Territories
     - Shapefile
     - Annually
   * - `ZNIEFF2 <https://inpn.mnhn.fr/telechargement/cartes-et-information-geographique/inv/znieff2>`_
     - INPN
     - Metropolitan France, Overseas Territories
     - Shapefile
     - Annually
   * - `ZNIEFF1 Mer <https://inpn.mnhn.fr/telechargement/cartes-et-information-geographique/inv/znieff1_mer>`_
     - INPN
     - Metropolitan France, Overseas Territories
     - Shapefile
     - Annually
   * - `ZNIEFF2 Mer <https://inpn.mnhn.fr/telechargement/cartes-et-information-geographique/inv/znieff2_mer>`_
     - INPN
     - Metropolitan France, Overseas Territories
     - Shapefile
     - Annually
   * - `Biotope Protection Orders <https://inpn.mnhn.fr/telechargement/cartes-et-information-geographique/ep/apb>`_
     - INPN
     - Metropolitan France, Overseas Territories
     - Shapefile
     - Annually
   * - `National Nature Reserves <https://inpn.mnhn.fr/telechargement/cartes-et-information-geographique/ep/rnn>`_
     - INPN
     - Metropolitan France, Overseas Territories
     - Shapefile
     - Annually
   * - `Regional Nature Reserves <https://inpn.mnhn.fr/telechargement/cartes-et-information-geographique/ep/rnr>`_
     - INPN
     - Metropolitan France, Overseas Territories
     - Shapefile
     - Annually
   * - `Biological Reserves <https://inpn.mnhn.fr/telechargement/cartes-et-information-geographique/ep/rb>`_
     - INPN
     - Metropolitan France, Overseas Territories
     - Shapefile
     - Annually

.. seealso::

	Refer to :ref:`this section <import-restricted-areas>` to learn more about loading restricted areas in your Geotrek-admin.

.. _sensitiveareas-source-list:

Sensitive areas
----------------

**Data source recommandation**

.. list-table:: Sensitive Natural Areas Data
   :widths: 20 15 20 15 15
   :header-rows: 1

   * - **Name**
     - **Provider**
     - **Coverage**
     - **Format**
     - **Update Frequency**
   * - `Sensitive Natural Areas <https://inpn.mnhn.fr/telechargement/cartes-et-information-geographique/ap/ens>`_
     - INPN
     - Metropolitan France, Overseas Territories
     - Shapefile
     - Annually

.. seealso::

	Refer to :ref:`this section <import-sensitive-areas>` to learn more about loading sensitive areas in your Geotrek-admin.