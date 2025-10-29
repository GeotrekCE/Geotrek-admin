.. command-load-import:

======================
The Load commands
======================

You can use some of Geotrek commands to import data from a vector or a raster file handled by `GDAL <https://gdal.org/drivers/vector/index.html>`_ (e.g.: ESRI Shapefile, GeoJSON, GeoPackage, GeoTIFF, etc.)

Possible data are : DEM, paths, cities, districts, restricted areas, POIs, infrastructures, signages.

You must use these commands to import spatial data because of the :ref:`dynamic segmentation <configuration-dynamic-segmentation>`, which will not be computed if you enter the data manually.

Here are the Geotrek commands available to import data from file:

- ``loaddem``
- ``loadpaths``
- ``loadcities``
- ``loaddistricts``
- ``loadrestrictedareas``
- ``loadpoi``
- ``loadinfrastructure``
- ``loadsignage``

Usually, these commands come with ability to match file attributes to model fields.

To get help about a command:

::

    sudo geotrek help <subcommand>


.. _import-dem-altimetry:

DEM
====

Load DEM
----------

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
		    --replace \
		    --update-altimetry

    .. md-tab-item:: Example with Docker

         .. code-block:: bash

		    docker compose run --rm web ./manage.py loaddem \
		    ./var/dem.tif \
		    --replace \
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

.. _import-paths:

Paths
=======

.. ns-only::

    ..

Load Paths
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
       * The ``--structure`` option requires an explicit value and cannot retrieve it from a field in the file.

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

Areas
======

.. abstract:: Keywords

   ``Biodiv'Sport``, ``command line``, ``import en ligne de commande``, ``shapefile``


.. _import-cities:

Load Cities
-------------

Refer to :ref:`this section <cities-source-list>` to learn about the available downloadable data sources.

.. example:: sudo geotrek help loadcities
    :collapsible:

    ::

      usage: manage.py loadcities [-h] [--code-attribute CODE]
                              [--name-attribute NAME] [--encoding ENCODING]
                              [--srid SRID] [--intersect] [--version]
                              [-v {0,1,2,3}] [--settings SETTINGS]
                              [--pythonpath PYTHONPATH] [--traceback]
                              [--no-color] [--force-color] [--skip-checks]
                              file_path

      Load Cities from a file within the spatial extent

      positional arguments:
        file_path             File's path of the cities

      optional arguments:
      -h, --help            show this help message and exit
      --code-attribute CODE, -c CODE
                            Name of the code's attribute inside the file
      --name-attribute NAME, -n NAME
                            Name of the name's attribute inside the file
      --encoding ENCODING, -e ENCODING
                            File encoding, default utf-8
      --srid SRID, -s SRID  File's SRID
      --intersect, -i       Check features intersect spatial extent and not only
                            within
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

    * **Optional fields** : Code, SRID, Encoding
    * **Required fields** : Name
    * **Geometric type** : Polygon
    * **Expected formats** (supported by GDAL) : Shapefile, Geojson, Geopackage
    * **Template** : :download:`cities.geojson <../files/import/cities.geojson>`
    * **Good to know** :
       * The default SRID code is 4326
       * The default encoding is UTF-8
       * Imported cities are unpublished by default
       * When importing a Geopackage, the first layer is always used

**Import command examples :**

.. md-tab-set::
    :name: cities-import-command-tabs

    .. md-tab-item:: Example with Debian

         .. code-block:: bash

          sudo geotrek loadcities \
          ./var/cities.geojson \
          --intersect \
          --srid=2154 \
          --encoding latin1 \
          --name-attribute nom \
          --code-attribute insee_com

    .. md-tab-item:: Example with Docker

        .. seealso::
	      Refer to :ref:`this section <docker-container-path>` to learn more about container path in Docker commands

        .. code-block:: bash


          docker compose run --rm web ./manage.py loadcities \
          ./var/cities.geojson \
          --intersect \
          --srid=2154 \
          --encoding latin1 \
          --name-attribute nom \
          --code-attribute insee_com

.. hint::

    The ``--intersect`` option allows you to import features outside the spatial extent of the project.

.. _import-districts:

Load Districts
----------------

Refer to :ref:`this section <districts-source-list>` to learn about the available downloadable data sources.

.. example:: sudo geotrek help loaddistricts
    :collapsible:

    ::

      usage: manage.py loaddistricts [-h] [--name-attribute NAME]
                                 [--encoding ENCODING] [--srid SRID]
                                 [--intersect] [--version] [-v {0,1,2,3}]
                                 [--settings SETTINGS] [--pythonpath PYTHONPATH]
                                 [--traceback] [--no-color] [--force-color]
                                 [--skip-checks]
                                 file_path

      Load Districts from a file within the spatial extent

      positional arguments:
        file_path             File's path of the districts

      optional arguments:
        -h, --help            show this help message and exit
        --name-attribute NAME, -n NAME
                              Name of the name's attribute inside the file
        --encoding ENCODING, -e ENCODING
                              File encoding, default utf-8
        --srid SRID, -s SRID  File's SRID
        --intersect, -i       Check features intersect spatial extent and not only
                              within
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
            -h, --help            show this help message and exit
            --name-attribute NAME, -n NAME
                                  Name of the name's attribute inside the file
            --encoding ENCODING, -e ENCODING
                                  File encoding, default utf-8
            --srid SRID, -s SRID  File's SRID
            --intersect, -i       Check features intersect spatial extent and not only within
            --version             show program's version number and exit
            -v {0,1,2,3}, --verbosity {0,1,2,3}
                                  Verbosity level; 0=minimal output, 1=normal output, 2=verbose output, 3=very verbose output
            --settings SETTINGS   The Python path to a settings module, e.g. "myproject.settings.main". If this isn't provided, the DJANGO_SETTINGS_MODULE environment variable will be used.
            --pythonpath PYTHONPATH
                                  A directory to add to the Python path, e.g. "/home/djangoprojects/myproject".
            --traceback           Raise on CommandError exceptions
            --no-color            Don't colorize the command output.
            --force-color         Force colorization of the command output.
            --skip-checks         Skip system checks.

.. note::

    * **Optional fields** : SRID, Encoding
    * **Required fields** : Name
    * **Geometric type** : Polygon
    * **Expected formats** (supported by GDAL) : Shapefile, Geojson, Geopackage
    * **Template** : :download:`districts.geojson <../files/import/districts.geojson>`
    * **Good to know** :
       * The default SRID code is 4326
       * The default encoding is UTF-8
       * Imported districts are unpublished by default
       * When importing a Geopackage, the first layer is always used

**Import command examples :**

.. md-tab-set::
    :name: districts-import-command-tabs

    .. md-tab-item:: Example with Debian

         .. code-block:: bash

          sudo geotrek loaddistricts \
          ./var/districts.geojson \
          --intersect \
          --srid=2154 \
          --encoding latin1 \
          --name-attribute nom

    .. md-tab-item:: Example with Docker

        .. seealso::
	      Refer to :ref:`this section <docker-container-path>` to learn more about container path in Docker commands

        .. code-block:: bash


          docker compose run --rm web ./manage.py loaddistricts \
          ./var/districts.geojson \
          --intersect \
          --srid=2154 \
          --encoding latin1 \
          --name-attribute nom

.. hint::

    The ``--intersect`` option allows you to import features outside the spatial extent of the project.

.. seealso::

    Refer to :ref:`this section <osm-parsers>` to import districts from OpenStreetMap.

.. _import-restricted-areas:

Load Restricted areas
----------------------

Refer to :ref:`this section <restrictedareas-source-list>` to learn about the available downloadable data sources.

.. example:: sudo geotrek help loadrestrictedareas
    :collapsible:

    ::

      usage: manage.py loadrestrictedareas [-h] [--name-attribute NAME]
                                       [--encoding ENCODING] [--srid SRID]
                                       [--intersect] [--version] [-v {0,1,2,3}]
                                       [--settings SETTINGS]
                                       [--pythonpath PYTHONPATH] [--traceback]
                                       [--no-color] [--force-color]
                                       [--skip-checks]
                                       file_path area_type

      Load Restricted Area from a file within the spatial extent

      positional arguments:
        file_path             File's path of the restricted area
        area_type             Type of restricted areas in the file

      positional arguments:
        file_path             File's path of the restricted area
        area_type             Type of restricted areas in the file

      optional arguments:
        -h, --help            show this help message and exit
        --name-attribute NAME, -n NAME
                              Name of the name's attribute inside the file
        --encoding ENCODING, -e ENCODING
                              File encoding, default utf-8
        --srid SRID, -s SRID  File's SRID
        --intersect, -i       Check features intersect spatial extent and not only
                              within
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

    * **Optional fields** : SRID, Encoding
    * **Required fields** : Name, Type zone
    * **Geometric type** : Polygon
    * **Expected formats** (supported by GDAL) : Shapefile, Geojson, Geopackage
    * **Template** : :download:`restrictedareas.geojson <../files/import/restrictedareas.geojson>`
    * **Good to know** :
       * The default SRID code is 4326
       * The default encoding is UTF-8
       * Imported restricted areas are unpublished by default
       * When importing a Geopackage, the first layer is always used
       * Only objects within the project bounding box can be imported

**Import command examples :**

.. md-tab-set::
    :name: restrictedareas-import-command-tabs

    .. md-tab-item:: Example with Debian

         .. code-block:: bash

          sudo geotrek loadrestrictedareas \
          ./var/restrictedareas.geojson \
          --intersect \
          "Réserve naturelle"  \
          --srid=2154 \
          --encoding latin1 \
          --name-attribute nom_site

    .. md-tab-item:: Example with Docker

        .. seealso::
	      Refer to :ref:`this section <docker-container-path>` to learn more about container path in Docker commands

        .. code-block:: bash


          docker compose run --rm web ./manage.py loadrestrictedareas \
          ./var/restrictedareas.geojson \
          --intersect \
          "Réserve naturelle"  \
          --srid=2154 \
          --encoding latin1 \
          --name-attribute nom_site

.. hint::

    The ``--intersect`` option allows you to import features outside the spatial extent of the project.

.. _import-pois:

POI
====

Load POI
----------

.. ns-detail::

    ..

.. example:: sudo geotrek help loadpoi
    :collapsible:

    ::

      usage: manage.py loadpoi [-h] [--encoding ENCODING] [--name-field NAME_FIELD]
                         [--type-field TYPE_FIELD]
                         [--description-field DESCRIPTION_FIELD]
                         [--name-default NAME_DEFAULT]
                         [--type-default TYPE_DEFAULT] [--version]
                         [-v {0,1,2,3}] [--settings SETTINGS]
                         [--pythonpath PYTHONPATH] [--traceback] [--no-color]
                         [--force-color] [--skip-checks]
                         point_layer

      Load a layer with point geometries in a model

      positional arguments:
        point_layer

      optional arguments:
      -h, --help            show this help message and exit
      --encoding ENCODING, -e ENCODING
                            File encoding, default utf-8
      --name-field NAME_FIELD, -n NAME_FIELD
                            Name of the field that contains the name attribute.
                            Required or use --name-default instead.
      --type-field TYPE_FIELD, -t TYPE_FIELD
                            Name of the field that contains the POI Type
                            attribute. Required or use --type-default instead.
      --description-field DESCRIPTION_FIELD, -d DESCRIPTION_FIELD
                            Name of the field that contains the description of the
                            POI (optional)
      --name-default NAME_DEFAULT
                            Default value for POI name. Use only if --name-field
                            is not set
      --type-default TYPE_DEFAULT
                            Default value for POI Type. Use only if --type-field
                            is not set
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

    * **Optional fields** : Description, SRID, Encoding
    * **Required fields** : Name, Type
    * **Geometric type** : Point
    * **Expected formats** (supported by GDAL) : Shapefile, Geojson, Geopackage
    * **Template** : :download:`poi.geojson <../files/import/poi.geojson>`
    * **Good to know** :
       * The SRID must be 4326
       * The default encoding is UTF-8
       * Imported POIs are unpublished by default
       * When importing a Geopackage, the first layer is always used

**Default values**

- When a default value is provided without a fieldname to import, the default value is set for all POIs objects.
- When a default value is provided in addition to a fieldname to import, it is used as a fallback for entries without the specified import field.

**Import command examples :**

.. md-tab-set::
    :name: poi-import-command-tabs

    .. md-tab-item:: Example with Debian

         .. code-block:: bash

          sudo geotrek loadpoi \
          ./var/poi.geojson \
          --encoding latin1 \
          --name-field name --name-default "Point d'intérêt" \
          --type-field type --type-default "Faune" \
          --description-field description


    .. md-tab-item:: Example with Docker

        .. seealso::
	      Refer to :ref:`this section <docker-container-path>` to learn more about container path in Docker commands

        .. code-block:: bash


          docker compose run --rm web ./manage.py loadpoi \
          ./var/poi.geojson \
          --encoding latin1 \
          --name-field name --name-default "Point d'intérêt" \
          --type-field type --type-default "Faune" \
          --description-field description

.. _import-infrastructure:

Infrastructure
===============

Load Infrastructure
--------------------

.. ns-detail::

    ..

.. example:: sudo geotrek help loadinfrastructure
    :collapsible:

    ::

      usage: manage.py loadinfrastructure [-h] [--use-structure]
                                      [--encoding ENCODING]
                                      [--name-field NAME_FIELD]
                                      [--name-default NAME_DEFAULT]
                                      [--type-field TYPE_FIELD]
                                      [--type-default TYPE_DEFAULT]
                                      [--category-field CATEGORY_FIELD]
                                      [--category-default CATEGORY_DEFAULT]
                                      [--condition-field CONDITION_FIELD]
                                      [--condition-default CONDITION_DEFAULT]
                                      [--structure-field STRUCTURE_FIELD]
                                      [--structure-default STRUCTURE_DEFAULT]
                                      [--description-field DESCRIPTION_FIELD]
                                      [--description-default DESCRIPTION_DEFAULT]
                                      [--year-field YEAR_FIELD]
                                      [--year-default YEAR_DEFAULT]
                                      [--eid-field EID_FIELD] [--version]
                                      [-v {0,1,2,3}] [--settings SETTINGS]
                                      [--pythonpath PYTHONPATH] [--traceback]
                                      [--no-color] [--force-color]
                                      [--skip-checks]
                                      point_layer

      Load a layer with point geometries and import features as infrastructures objects
      (expected formats: shapefile or geojson)

      positional arguments:
        point_layer

      optional arguments:
      -h, --help            show this help message and exit
      --use-structure       If set the given (or default) structure is used to
                            select or create conditions and types of
                            infrastructures.
      --encoding ENCODING, -e ENCODING
                            File encoding, default utf-8
      --name-field NAME_FIELD, -n NAME_FIELD
                            The field to be imported as the `name` of the
                            infrastructure
      --name-default NAME_DEFAULT
                            Default name for all infrastructures, fallback for
                            entries without a name
      --type-field TYPE_FIELD, -t TYPE_FIELD
                            The field to select or create the type value of the
                            infrastructure (field `InfrastructureType.label`)
      --type-default TYPE_DEFAULT
                            Default type for all infrastructures, fallback for
                            entries without a type.
      --category-field CATEGORY_FIELD, -i CATEGORY_FIELD
                            The field to select or create the type value of the
                            infrastructure (field `InfrastructureType.type`)
      --category-default CATEGORY_DEFAULT
                            Default category for all infrastructures, "B" by
                            default. Fallback for entries without a category
      --condition-field CONDITION_FIELD, -c CONDITION_FIELD
                            The field to select or create the condition value of
                            the infrastructure (field
                            `InfrastructureCondition.label`)
      --condition-default CONDITION_DEFAULT
                            Default condition for all infrastructures, fallback
                            for entries without a category
      --structure-field STRUCTURE_FIELD, -s STRUCTURE_FIELD
                            The field to be imported as the structure of the
                            infrastructure
      --structure-default STRUCTURE_DEFAULT
                            Default Structure for all infrastructures
      --description-field DESCRIPTION_FIELD, -d DESCRIPTION_FIELD
                            The field to be imported as the description of the
                            infrastructure
      --description-default DESCRIPTION_DEFAULT
                            Default description for all infrastructures, fallback
                            for entries without a description
      --year-field YEAR_FIELD, -y YEAR_FIELD
                            The field to be imported as the `implantation_year` of
                            the infrastructure
      --year-default YEAR_DEFAULT
                            Default year for all infrastructures, fallback for
                            entries without a year
      --eid-field EID_FIELD
                            The field to be imported as the `eid` of the
                            infrastructure (external ID)
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

    * **Optional fields** : Structure, Description, Status, Year, External ID, SRID, Encoding
    * **Required fields** : Name, Type, Category
    * **Geometric type** : Point
    * **Expected formats** (supported by GDAL) : Shapefile, Geojson, Geopackage
    * **Template** : :download:`infrastructure.geojson <../files/import/infrastructure.geojson>`
    * **Good to know** :
       * The SRID must be 4326
       * The default encoding is UTF-8
       * Imported infrastructures are unpublished by default
       * When importing a Geopackage, the first layer is always used
       * The command will select or create ``InfrastructureType`` values based on the ``type-field`` argument, taking the default value "A" for the category

**Required fields**

The following fields are mandatory to create an Infrastructure object: ``name``, ``type`` and ``category``. For each of those fields either an import field and/or a default value MUST be provided. If the command is unable to determine values for those fields for a given layer, the layer is skipped with an error message.

**Default values**

- When a default value is provided without a fieldname to import, the default value is set for all Infrastructure objects.
- When a default value is provided in addition to a fieldname to import, it is used as a fallback for entries without the specified import field.

**Selection and addition of parameterized values**

Infrastructure objects have several values from Geotrek's parameterized value sets:

- ``type`` from ``InfrastructureType`` values (and ``category`` which is implied by the ``type`` value),
- ``condition`` from ``InfrastructureCondition`` values.

New parameterized values are created and added to Geotrek-admin if necessary. The command checks if the imported ``type`` value already exists by looking for an ``InfrastructureType`` with the right ``type`` + ``category``.

- ``A`` category value stands for Building
- ``E`` category value stands for Equipment

.. md-tab-set::
    :name: infrastructure-import-type-command-tabs

    .. md-tab-item:: Example with Debian

         .. code-block:: bash

          sudo geotrek loadinfrastructure  --type-field "type"  --category-field "cat" [...]

    .. md-tab-item:: Example with Docker

         .. code-block:: bash

          docker compose run --rm web ./manage.py loadinfrastructure --type-field "type"  --category-field "cat" [...]

**Import command examples:**

.. md-tab-set::
    :name: infrastructures-import-command-tabs

    .. md-tab-item:: Example with Debian

         .. code-block:: bash

          sudo geotrek loadinfrastructure \
          ./var/infrastructure.geojson \
          --encoding latin1 \
          --name-field name --name-default "Banc" \
          --type-field type --type-default "Banc" \
          --category-field categorie --category-default "E" \
          --description-field descriptio --description-default "Banc confortable" \
          --condition-field etat --condition-default "Bon état" \
          --structure-field structure --structure-default "Ma structure" \
          --year-field annee --year-default "2024" \
          --eid-field id

    .. md-tab-item:: Example with Docker

        .. seealso::
	      Refer to :ref:`this section <docker-container-path>` to learn more about container path in Docker commands

        .. code-block:: bash


          docker compose run --rm web ./manage.py loadinfrastructure \
          ./var/infrastructure.geojson \
          --encoding latin1 \
          --name-field name --name-default "Banc" \
          --type-field type --type-default "Banc" \
          --category-field categorie --category-default "E" \
          --description-field descriptio --description-default "Banc confortable" \
          --condition-field etat --condition-default "Bon état" \
          --structure-field structure --structure-default "Ma structure" \
          --year-field annee --year-default "2024" \
          --eid-field id

.. _import-signage:

Signage
========

Load Signage
-------------

.. ns-detail::

    ..

.. example:: sudo geotrek help loadsignage
    :collapsible:

    ::

      usage: manage.py loadsignage [-h] [--use-structure] [--encoding ENCODING]
                               [--name-field NAME_FIELD]
                               [--type-field TYPE_FIELD]
                               [--condition-field CONDITION_FIELD]
                               [--manager-field MANAGER_FIELD]
                               [--sealing-field SEALING_FIELD]
                               [--structure-field STRUCTURE_FIELD]
                               [--description-field DESCRIPTION_FIELD]
                               [--year-field YEAR_FIELD]
                               [--code-field CODE_FIELD] [--eid-field EID_FIELD]
                               [--type-default TYPE_DEFAULT]
                               [--name-default NAME_DEFAULT]
                               [--condition-default CONDITION_DEFAULT]
                               [--manager-default MANAGER_DEFAULT]
                               [--sealing-default SEALING_DEFAULT]
                               [--structure-default STRUCTURE_DEFAULT]
                               [--description-default DESCRIPTION_DEFAULT]
                               [--year-default YEAR_DEFAULT]
                               [--code-default CODE_DEFAULT] [--version]
                               [-v {0,1,2,3}] [--settings SETTINGS]
                               [--pythonpath PYTHONPATH] [--traceback]
                               [--no-color] [--force-color] [--skip-checks]
                               point_layer


      Load a layer with point geometries in te structure model

      positional arguments:
        point_layer

      optional arguments:
      -h, --help            show this help message and exit
      --use-structure       Allow to use structure for condition and type of
                            infrastructures
      --encoding ENCODING, -e ENCODING
                            File encoding, default utf-8
      --name-field NAME_FIELD, -n NAME_FIELD
                            Name of the field that will be mapped to the Name
                            field in Geotrek
      --type-field TYPE_FIELD, -t TYPE_FIELD
                            Name of the field that will be mapped to the Type
                            field in Geotrek
      --condition-field CONDITION_FIELD, -c CONDITION_FIELD
                            Name of the field that will be mapped to the Condition
                            field in Geotrek
      --manager-field MANAGER_FIELD, -m MANAGER_FIELD
                            Name of the field that will be mapped to the Manager
                            field in Geotrek
      --sealing-field SEALING_FIELD
                            Name of the field that will be mapped to the sealing
                            field in Geotrek
      --structure-field STRUCTURE_FIELD, -s STRUCTURE_FIELD
                            Name of the field that will be mapped to the Structure
                            field in Geotrek
      --description-field DESCRIPTION_FIELD, -d DESCRIPTION_FIELD
                            Name of the field that will be mapped to the
                            Description field in Geotrek
      --year-field YEAR_FIELD, -y YEAR_FIELD
                            Name of the field that will be mapped to the Year
                            field in Geotrek
      --code-field CODE_FIELD
                            Name of the field that will be mapped to the Code
                            field in Geotrek
      --eid-field EID_FIELD
                            Name of the field that will be mapped to the External
                            ID in Geotrek
      --type-default TYPE_DEFAULT
                            Default value for Type field
      --name-default NAME_DEFAULT
                            Default value for Name field
      --condition-default CONDITION_DEFAULT
                            Default value for Condition field
      --manager-default MANAGER_DEFAULT
                            Default value for the Manager field
      --sealing-default SEALING_DEFAULT
                            Default value for the Sealing field
      --structure-default STRUCTURE_DEFAULT
                            Default value for Structure field
      --description-default DESCRIPTION_DEFAULT
                            Default value for Description field
      --year-default YEAR_DEFAULT
                            Default value for Year field
      --code-default CODE_DEFAULT
                            Default value for Code field
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

    * **Optional fields** : Comment, SRID, Encoding
    * **Required fields** : Structure, Name
    * **Geometric type** : Point
    * **Expected formats** (supported by GDAL) : Shapefile, Geojson, Geopackage
    * **Template** : :download:`signage.geojson <../files/import/signage.geojson>`
    * **Good to know** :
       * The default SRID code is 4326
       * The default encoding is UTF-8
       * Imported signage are unpublished by default
       * When importing a Geopackage, the first layer is always used

**Default values**

- When a default value is provided without a fieldname to import, the default value is set for all Signage objects.
- When a default value is provided in addition to a fieldname to import, it is used as a fallback for entries without the specified import field.

**Import command examples:**

.. md-tab-set::
    :name: signage-import-command-tabs

    .. md-tab-item:: Example with Debian

         .. code-block:: bash

          sudo geotrek loadsignage \
          ./var/signage.geojson \
          --encoding latin1 \
          --name-field name \
          --type-field type --type-default "Directionnelle" \
          --condition-field etat --condition-default "Bon état" \
          --manager-field gestionnaire \
          --sealing-field scellement --sealing-default "Planté" \
          --structure-field structure \
          --description-field description --description-default "Poteau planté" \
          --year-field annee --year-default "2024" \
          --code-field code --code-default "81150_PR2_P1" \
          --eid-field id

    .. md-tab-item:: Example with Docker

        .. seealso::
	      Refer to :ref:`this section <docker-container-path>` to learn more about container path in Docker commands

        .. code-block:: bash


          docker compose run --rm web ./manage.py loadsignage \
          ./var/signage.geojson \
          --encoding latin1 \
          --name-field name \
          --type-field type --type-default "Directionnelle" \
          --condition-field etat --condition-default "Bon état" \
          --manager-field gestionnaire \
          --sealing-field scellement --sealing-default "Planté" \
          --structure-field structure \
          --description-field description --description-default "Poteau planté" \
          --year-field annee --year-default "2024" \
          --code-field code --code-default "81150_PR2_P1" \
          --eid-field id

.. important::

    Blades are not yet supported, therefore this command only imports signages in the database.

