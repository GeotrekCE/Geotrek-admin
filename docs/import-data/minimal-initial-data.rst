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

.. _import-dem-altimetry:

Load DEM
---------

.. example:: sudo geotrek help loaddem
    :collapsible:

    ::

      usage: manage.py loaddem [-h] [--replace]
      					 [--update-altimetry]
      					 [--version]
                         [-v {0,1,2,3}] [--settings SETTINGS]
                         [--pythonpath PYTHONPATH] [--traceback] [--no-color]
                         [--force-color] [--skip-checks]
                         dem_path

	  Load DEM data (projecting and clipping it if necessary). You may need to create a GDAL Virtual Raster if your DEM is composed of several files.

	  positional arguments:
	      dem_path

	  optional arguments:
	  -h, --help            show this help message and exit
	  --replace             Replace existing DEM if any.
	  --update-altimetry    Update altimetry of all 3D geometries, /!\ This option
		                        takes lot of time to perform
	  --version             Show program's version number and exit.
	  -v {0,1,2,3}, --verbosity {0,1,2,3}
		                        Verbosity level; 0=minimal output, 1=normal output,
		                        2=verbose output, 3=very verbose output
	  --settings SETTINGS   The Python path to a settings module, e.g.
		                        "myproject.settings.main". If this isn't provided, the
		                        DJANGO_SETTINGS_MODULE environment variable will be
		                        used.
	  --pythonpath PYTHONPATH
		                        A directory to add to the Python path, e.g.
		                        "/home/djangoprojects/myproject".
	  --traceback           Raise on CommandError exceptions.
	  --no-color            Don't colorize the command output.
	  --force-color         Force colorization of the command output.
	  --skip-checks         Skip system checks.

**Import command examples :**

.. md-tab-set::
    :name: dem-import-command-tabs

    .. md-tab-item:: Example with Debian

         .. code-block:: bash

		    sudo geotrek loaddem \
		    ./var/dem.tif \
		    --update-altimetry

    .. md-tab-item:: Example with Docker

         .. code-block:: bash

		    docker compose run --rm web ./manage.py loaddem \
		    ./var/dem.tif \
		    --update-altimetry

.. _docker-container-path:

.. IMPORTANT::
   When running a command via Docker, all file paths must refer to locations **inside the container**, not on the host machine. The ``var`` folder is mounted as a volume in the container, with the following mapping:
   ``/path-on-host/var`` → ``/opt/geotrek-admin/var``.

   So you just need to place the file in the ``var`` directory on the host, and it will be accessible from inside the container at the expected path.

   👉 In short:
   Docker commands in Geotrek use **container paths**.
   The `var` folder is shared between the host and the container, so any file placed in `var` can be accessed using either ``./var/...`` or ``/opt/geotrek-admin/var/...`` **inside the container**.

   Example : ``./var/dem.tif`` or ``/opt/geotrek-admin/var/dem.tif``

Paths
=======

.. abstract:: Keywords

   ``command line``, ``import en ligne de commande``, ``QGIS``


.. ns-only::

    ..

Requirements
-------------

.. important::
    With :ref:`dynamic segmentation <configuration-dynamic-segmentation>`, importing paths is very risky if paths are already present in the same area in Geotrek,
    it is only safe for an area where no path is already created.

    Indeed, if you import paths where there are existing paths, treks, POIs or trails linked topology might be impacted.

Before import paths layer, it is important to prepare them. Paths must be:

- valid geometry
- simple geometry (no intersection)
- all intersections must cut the paths
- not double or covering others

Clean paths
------------

We use QGis to clean a path layer, with plugin Grass.
Here are the operations:

- check the SRID (must be the same as in Geotrek)

- vectors → geometric tools → "collect geometries"

- vectors → geometric tools → "group"

- clean geometries
    - search "v_clean" in "Processing toolbox"
    - select following options in cleaning tool: break, snap, duplicate (ou rmdup), rmline, rmdangle, chdangle, bpol, prune
    - in threshold enter 2,2,2,2,2,2,2,2 (2 meters for each option)

- delete duplicate geometries
    - search "duplicate" in "Processing toolbox"

- regroup lines
    - search "v.build.polyline" in "Processing toolbox")
    - select "first" in "Category number mode"

There are two ways to import path : importing your shapefile with command line,
or `via QGis following this blog post <https://makina-corpus.com/sig-webmapping/importer-une-couche-de-troncons-dans-geotrek>`_.

**To import a shapefile containing your paths, use the command** ``loadpaths``

Load paths
-----------

.. example:: sudo geotrek help loadpaths
    :collapsible:

    ::

      usage: manage.py loadpaths [-h] [--structure STRUCTURE]
                             [--name-attribute NAME]
                             [--comments-attribute [COMMENT [COMMENT ...]]]
                             [--encoding ENCODING] [--srid SRID] [--intersect]
                             [--fail] [--dry] [--version] [-v {0,1,2,3}]
                             [--settings SETTINGS] [--pythonpath PYTHONPATH]
                             [--traceback] [--no-color] [--force-color]
                             [--skip-checks]
                             file_path

      Load a layer with point geometries in a model

      positional arguments:
        point_layer

      optional arguments:
      -h, --help            show this help message and exit
      --structure STRUCTURE
                            Define the structure
      --name-attribute NAME, -n NAME
                            Name of the name's attribute inside the file
      --comments-attribute [COMMENT [COMMENT ...]], -c [COMMENT [COMMENT ...]]
      --encoding ENCODING, -e ENCODING
                            File encoding, default utf-8
      --srid SRID, -s SRID  File's SRID
      --intersect, -i       Check paths intersect spatial extent and not only
                            within
      --fail, -f            Allows to grant fails
      --dry, -d             Do not change the database, dry run. Show the number
                            of fail and objects potentially created
      --version             Show program's version number and exit.
      -v {0,1,2,3}, --verbosity {0,1,2,3}
                            Verbosity level; 0=minimal output, 1=normal output,
                            2=verbose output, 3=very verbose output
      --settings SETTINGS   The Python path to a settings module, e.g.
                            "myproject.settings.main". If this isn't provided, the
                            DJANGO_SETTINGS_MODULE environment variable will be
                            used.
      --pythonpath PYTHONPATH
                            A directory to add to the Python path, e.g.
                            "/home/djangoprojects/myproject".
      --traceback           Raise on CommandError exceptions.
      --no-color            Don't colorize the command output.
      --force-color         Force colorization of the command output.
      --skip-checks         Skip system checks.

.. note::

    * **Optional fields** : Name, Comment, SRID, Encoding
    * **Required fields** : Structure
    * **Geometric type** : Linestring
    * **Expected formats** (supported by GDAL) : Shapefile, Geojson, Geopackage
    * **Template** : :download:`paths.geojson <../files/import/paths.geojson>`
    * **Good to know** :
       * The default SRID code is 4326
       * The default encoding is UTF-8
       * When importing a Geopackage, the first layer is always used
       * The `--structure` requires an existing value and cannot retrieve it from a field in the file.

**Import command examples :**

.. md-tab-set::
    :name: path-import-command-tabs

    .. md-tab-item:: Example with Debian

         .. code-block:: bash

          sudo geotrek loadpaths \
          ./var/paths.geojson \
          --srid=2154 \
          --encoding latin1 \
          --structure "DEMO" \
          --name-attribute id \
          --comments-attribute commentaire


    .. md-tab-item:: Example with Docker

        .. seealso::
	      Refer to :ref:`this section <docker-container-path>` to learn more about container path in Docker commands

        .. code-block:: bash

          docker compose run --rm web ./manage.py loadpaths \
          ./var/paths.geojson \
          --srid=2154 \
          --encoding latin1 \
          --structure "DEMO" \
          --name-attribute id \
          --comments-attribute commentaire


.. note::

  After importing a large quantity of paths, it is recommended to pre-generate the paths graph needed for the routing.

  This action is not mandatory, but will reduce the time needed for the first routing following the import.

  To pre-generate the graph, use the ``generate_pgr_network_topology`` command:

  .. md-tab-set::
      :name: path-import-command-regenerate-topologytabs

      .. md-tab-item:: Example with Debian

          .. code-block:: bash

            sudo geotrek generate_pgr_network_topology

      .. md-tab-item:: Example with Docker

          .. code-block:: bash

            docker compose run --rm web ./manage.py generate_pgr_network_topology

Get OpenStreetMap paths
------------------------

You can use the ``osm-paths`` tool to download OSM paths data via the overpass API. This tool converts paths into linestrings and exports them to GeoJSON.

For more information, refer to the `osm-paths documentation <https://github.com/makinacorpus/osm-paths>`_

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