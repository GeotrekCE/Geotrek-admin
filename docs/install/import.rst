===========
Import data
===========

Import paths
============

.. danger::
    With dynamic segmentation, importing paths is very risky if paths are already present in the same area in Geotrek,
    it is only safe for an area where no path is already created.

    Indeed, if you import paths where there are existing paths, treks, POIs or trails linked topology might be impacted.

Before import paths layer, it is important to prepare them. Paths must be:

- valid geometry
- simple geometry (no intersection)
- all intersections must cut the paths
- not double or covering others

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

To import a shapefile containing your paths, use the command ``loadpaths``::

    sudo geotrek loadpaths {Troncons.shp} \
        --srid=2154 --comments-attribute IT_VTT IT_EQ IT_PEDEST \
        --encoding latin9 -i


Import data from touristic data systems (SIT)
=============================================

Configure APIDAE (ex-SITRA) import
----------------------------------

To import touristic content from APIDAE (ex-SITRA), edit ``/opt/geotrek-admin/var/conf/parsers.py`` file with the following content:

::

    from geotrek.tourism.parsers import TouristicContentApidaeParser

    class HebergementParser(TouristicContentApidaeParser):
        label = "Hébergements"
        api_key = 'xxxxxxxx'
        project_id = 9999
        selection_id = 99999
        category = "Hébergement"
        type1 = ["Camping"]
        type2 = ["3 étoiles", "Tourisme et Handicap"]  # just remove this line if no type2

Then set up appropriate values:

* ``label`` at your convenience,
* ``api_key``, ``project_id`` and ``selection_id`` according to your APIDAE (ex-SITRA) configuration
* ``category``, ``type1`` and ``type2`` (optional) to select in which Geotrek category/type imported objects should go
* You can add ``delete = True`` in your class if you want to delete objects in Geotrek databases that has been deleted in your Apidae selection. It will only delete objects that match with your class settings (category, types, portal, provider...)
* You can also use the class ``HebergementParser`` if you only import accomodations
* See https://github.com/GeotrekCE/Geotrek-admin/blob/master/geotrek/tourism/parsers.py for details about Parsers

You can duplicate the class. Each class must have a different name.
Don't forget the u character before strings if they contain non-ascii characters.

To apply changes, you may have to run ``sudo service geotrek restart``.


Configure Marque Esprit Parc import
-----------------------------------

To import touristic content from Esprit Parc national database, create (or update) ``/opt/geotrek-admin/var/conf/parsers.py`` file with the following content:

::

    from geotrek.tourism.parsers import EspritParcParser

    class XXXEspritParcParser(EspritParcParser):
        label = "Marque Esprit Parc"
        url = "https://gestion.espritparcnational.com/ws/?f=getProduitsSelonParc&codeParc=XXX"

Then set up appropriate values:

* ``XXX`` by unique national park code (ex: PNE)

You can duplicate the class. Each class must have a different name.
Don't forget the u character before strings if they contain non-ascii characters.

In this case categories and types in Geotrek database have to be the same as in Esprit parc database. Otherwise missing categories and types will be created in Geotrek database.

Imported contents will be automatically published and approved. 

If you use an url that filters a unique category, you can change its name. Example to get only Honey products and set the Geotrek category and type in which import them:

::

    class MielEspritParcParser(EspritParcParser):
        label = "Miel Esprit Parc national"
        url = "https://gestion.espritparcnational.com/ws/?f=getProduitsSelonParc&codeParc=XXX&typologie=API"
        constant_fields = {
            'category': "GeotrekCategoryName",
            'published': True,
            'approved': True,
            'deleted': False,
        }
        m2m_constant_fields = {
            'type1': "GeotrekTypeName",
        }

URL to get Esprit parc types: `https://gestion.espritparcnational.com/ws/?f=getTypologieProduits`.


Sensitive areas import
----------------------

When sensitive areas module is enabled, Geotrek provides 3 parsers to import data:

* Import sensitive areas from http://biodiv-sports.fr (``geotrek.sensitivity.parsers.BiodivParser``). By default this
  parser imports all sensitive areas in configured spatial extent.
* Import species sensitive areas from a ziped shapefile. Imported field names are: ``espece`` (required), ``contact``
  and ``descriptio``.
  Species with corresponding names have to be created manually before import.
* Import regulatory sensitive areas from a ziped shapefile. Imported field names are: ``nom`` (required), ``contact``,
  ``descriptio``, ``periode`` (month numbers separated with comas), ``pratiques`` (separated with comas), and ``url``.
  Practices with corresponding names have to be created manually before import.

You can start imports from "Import" menu or from command line. You can override them in your ``var/conf/parsers.py``
file.


Multiple imports
----------------

When you need to import data for the same object found in 2 different parsers, you can to force the aggregation of both values in many to many relationship case.
It can be interesting with portals for example.

Param for the aggregation : ``m2m_aggregate_fields``

Here is an example with 2 parsers :

::

    class Portal_1Parser(XXXParser):
        portal = "portal_1"

    class AggregateParser(XXXParser):
        portal = "portal_2"
        m2m_aggregate_fields = ["portal"]

Then, when you import the first parser ``Portal_1Parser``, you get multiple objects with ``portal_1`` as portal.
If any object of the ``Portal_1Parser`` is also in ``AggregateParser``, fields in ``m2m_aggregate_fields`` will have their values not be replaced but aggregated.
Then your object in both portals will have as portal: ``portal_1, portal_2``

* Here in this example whenever you import the first parser ``Portal_1Parser``, portals are replaced because ``m2m_aggregate_fields`` is not filled. Then, be careful to import parsers in the right order or add the param ``m2m_aggregate_fields`` on all parsers.

If you need to cancel the aggregation of portals, remove param ``m2m_aggregate_fields``.


Importing from multiple sources with deletion
----------------

When importing data for the same model using two (or more) different sources, the ``provider`` field should be used to differenciate between sources, allowing to enable object deletion with ``delete = True`` without causing the last parser to delete objects created by preceeding parsers.

In the following example, ``Provider_1Parser`` and ``Provider_2Parser`` will each import their objects, set the ``provider`` field on these objects, and only delete objects that disappeared from their respective source since last parsing.

::

    class Provider_1Parser(XXXXParser):
        delete = True
        provider = "provider_1"

    class Provider_2Parser(XXXParser):
        delete = True
        provider = "provider_2"


.. danger::
    It is recommended to use ``provider`` from the first import - Do not add a ``provider`` field to preexisting parsers that already imported objects, or you will have to manually set the same value for ``provider`` on all objects already created by this parser. 


.. danger::
    If a parser does not have a ``provider`` value, it will not take providers into account, meaning that it could delete objects from preceeding parsers even if these other parsers do have a ``provider`` themselves.


The following example would cause ``NoProviderParser`` to delete objects from ``Provider_2Parser`` and ``Provider_1Parser``.

::

    class Provider_1Parser(XXXXParser):
        delete = True
        provider = "provider_1"

    class Provider_2Parser(XXXParser):
        delete = True
        provider = "provider_2"

    class NoProviderParser(XXXParser):
        delete = True
        provider = None       (default)


Generic settings for your parser
--------------------------------

This settings may be overriden when you define a new parser:

- ``label`` parser display name (default: ``None``)
- ``model`` import content with this model (default: ``None``)
- ``filename`` file imported if no url (default: ``None``)
- ``url`` flow url imported from if no filename (default: ``None``)
- ``simplify_tolerance`` (default: ``0``)  # meters
- ``update_only`` don't create new contents (default: ``False``)
- ``delete`` (default: ``False``)
- ``duplicate_eid_allowed`` if True, allows differents contents with same eid (default: ``False``)
- ``fill_empty_translated_fields`` if True, fills empty translated fields with same value  (default: ``False``)
- ``warn_on_missing_fields`` (default: ``False``)
- ``warn_on_missing_objects`` (default: ``False``)
- ``separator`` (default: ``'+'``)
- ``eid`` field name for eid (default: ``None``)
- ``provider`` (default: ``None``)
- ``fields`` (default: ``None``)
- ``m2m_fields``  (default: ``{}``)
- ``constant_fields`` (default: ``{}``)
- ``m2m_constant_fields`` (default: ``{}``)
- ``m2m_aggregate_fields`` (default: ``[]``)
- ``non_fields`` (default: ``{}``)
- ``natural_keys`` (default: ``{}``)
- ``field_options`` (default: ``{}``)
- ``default_language`` use another default language for this parser (default: ``None``)


Start import from command line
------------------------------

Just run:

::

    sudo geotrek import HebergementParser

Change ``HebergementParser`` to match one of the class names in ``var/conf/parsers.py`` file.
You can add ``-v2`` parameter to make the command more verbose (show progress).
Thank to ``cron`` utility you can configure automatic imports.


Start import from Geotrek-admin UI
----------------------------------

Open the top right menu and clic on ``imports``.


Import data from a remote Geotrek instance
==========================================

Importing from a Geotrek instance works the same way as from SIT.
A usecase for this is to aggregate data from several Geotrek-admin instance.

.. danger::
    Importing data from a remote Geotrek instance does not work with dynamic segmentation, your instance where you import data
    must have dynamic segmentation disabled.


For example, to import treks from another instance,
edit ``/opt/geotrek-admin/var/conf/parsers.py`` file with the following content:

::

    class DemoGeotrekTrekParser(BaseGeotrekTrekParser):
        url = "https://remote-geotrek-admin.net"  # replace url with remote instance url
        delete = False
        field_options = {
            'difficulty': {'create': True, },
            'route': {'create': True, },
            'themes': {'create': True},
            'practice': {'create': True},
            'accessibilities': {'create': True},
            'networks': {'create': True},
            'geom': {'required': True},
            'labels': {'create': True},
        }

Then run in command line

::

    sudo geotrek import DemoGeotrekTrekParser

Treks are now imported into your own instance.


Import other datas from a file
==============================

You can also use some of Geotrek commands to import data from a vector file handled by GDAL (https://gdal.org/drivers/vector/index.htm) (e.g.: ESRI Shapefile, GeoJSON, GeoPackage etc.)

Possible data are e.g.: POI, infrastructures, signages, cities, districts, restricted areas, dives, paths.

You must use these commands to import spatial data because of the dynamic segmentation, which will not be computed if you enter the data manually. 

Here are the Geotrek commands available to import data from file:

- ``loaddem``
- ``loadpoi``
- ``loaddive``
- ``loadinfrastructure``
- ``loadsignage``
- ``loadcities``
- ``loaddistricts``
- ``loadrestrictedareas``

Usually, these commands come with ability to match file attributes to model fields.

To get help about a command:

::

    sudo geotrek help <subcommand>


Import DEM (altimetry)
----------------------

``sudo geotrek help loaddem``

::

    usage: manage.py loaddem [-h] [--replace] [--update-altimetry] [--version] [-v {0,1,2,3}] [--settings SETTINGS] [--pythonpath PYTHONPATH] [--traceback] [--no-color] [--force-color]
                         [--skip-checks]
                         dem_path

    Load DEM data (projecting and clipping it if necessary). You may need to create a GDAL Virtual Raster if your DEM is composed of several files.

    positional arguments:
      dem_path

    optional arguments:
      -h, --help            show this help message and exit
      --replace             Replace existing DEM if any.
      --update-altimetry    Update altimetry of all 3D geometries, /!\ This option takes lot of time to perform
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


Import POIs
-----------

``sudo geotrek help loadpoi``

::

    usage: manage.py loadpoi [-h] [--encoding ENCODING] [--name-field NAME_FIELD] [--type-field TYPE_FIELD] [--description-field DESCRIPTION_FIELD]
                             [--name-default NAME_DEFAULT] [--type-default TYPE_DEFAULT] [--version] [-v {0,1,2,3}] [--settings SETTINGS] [--pythonpath PYTHONPATH]
                             [--traceback] [--no-color] [--force-color] [--skip-checks]
                             point_layer

    Load a layer with point geometries in a model

    positional arguments:
      point_layer

    optional arguments:
      -h, --help            show this help message and exit
      --encoding ENCODING, -e ENCODING
                            File encoding, default utf-8
      --name-field NAME_FIELD, -n NAME_FIELD
                            Name of the field that contains the name attribute. Required or use --name-default instead.
      --type-field TYPE_FIELD, -t TYPE_FIELD
                            Name of the field that contains the POI Type attribute. Required or use --type-default instead.
      --description-field DESCRIPTION_FIELD, -d DESCRIPTION_FIELD
                            Name of the field that contains the description of the POI (optional)
      --name-default NAME_DEFAULT
                            Default value for POI name. Use only if --name-field is not set
      --type-default TYPE_DEFAULT
                            Default value for POI Type. Use only if --type-field is not set
      --version             show program's version number and exit
      -v {0,1,2,3}, --verbosity {0,1,2,3}
                            Verbosity level; 0=minimal output, 1=normal output, 2=verbose output, 3=very verbose output
      --settings SETTINGS   The Python path to a settings module, e.g. "myproject.settings.main". If this isn't provided, the DJANGO_SETTINGS_MODULE environment variable will
                            be used.
      --pythonpath PYTHONPATH
                            A directory to add to the Python path, e.g. "/home/djangoprojects/myproject".
      --traceback           Raise on CommandError exceptions
      --no-color            Don't colorize the command output.
      --force-color         Force colorization of the command output.
      --skip-checks         Skip system checks.



Import Infrastructure
---------------------

``sudo geotrek help loadinfrastructure``

::

    usage: manage.py loadinfrastructure [-h] [--use-structure] [--encoding ENCODING] [--name-field NAME_FIELD] [--type-field TYPE_FIELD] [--category-field CATEGORY_FIELD]
                                        [--condition-field CONDITION_FIELD] [--structure-field STRUCTURE_FIELD] [--description-field DESCRIPTION_FIELD] [--year-field YEAR_FIELD]
                                        [--type-default TYPE_DEFAULT] [--category-default CATEGORY_DEFAULT] [--name-default NAME_DEFAULT] [--condition-default CONDITION_DEFAULT]
                                        [--structure-default STRUCTURE_DEFAULT] [--description-default DESCRIPTION_DEFAULT] [--eid-field EID_FIELD] [--year-default YEAR_DEFAULT]
                                        [--version] [-v {0,1,2,3}] [--settings SETTINGS] [--pythonpath PYTHONPATH] [--traceback] [--no-color] [--force-color] [--skip-checks]
                                        point_layer

    Load a layer with point geometries in te structure model

    positional arguments:
      point_layer

    optional arguments:
      -h, --help            show this help message and exit
      --use-structure       Allow to use structure for condition and type of infrastructures
      --encoding ENCODING, -e ENCODING
                            File encoding, default utf-8
      --name-field NAME_FIELD, -n NAME_FIELD
                            Base url
      --type-field TYPE_FIELD, -t TYPE_FIELD
                            Base url
      --category-field CATEGORY_FIELD, -i CATEGORY_FIELD
                            Base url
      --condition-field CONDITION_FIELD, -c CONDITION_FIELD
                            Base url
      --structure-field STRUCTURE_FIELD, -s STRUCTURE_FIELD
                            Base url
      --description-field DESCRIPTION_FIELD, -d DESCRIPTION_FIELD
                            Base url
      --year-field YEAR_FIELD, -y YEAR_FIELD
                            Base url
      --type-default TYPE_DEFAULT
                            Default type of infrastructure, it will create the type if it doesn't exist
      --category-default CATEGORY_DEFAULT
                            Category by default for all infrastructures, B by default
      --name-default NAME_DEFAULT
                            Base url
      --condition-default CONDITION_DEFAULT
                            Default Condition for all infrastructures, it will create the condition if it doesn't exist
      --structure-default STRUCTURE_DEFAULT
                            Default Structure for all infrastructures
      --description-default DESCRIPTION_DEFAULT
                            Default description for all infrastructures
      --eid-field EID_FIELD
                            External ID field
      --year-default YEAR_DEFAULT
                            Default year for all infrastructures
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


Import Dive
-----------

``sudo geotrek help loaddive``

::

    usage: manage.py loaddive [-h] [--encoding ENCODING] [--name-field NAME_FIELD] [--depth-field DEPTH_FIELD] [--practice-default PRACTICE_DEFAULT]
                              [--structure-default STRUCTURE_DEFAULT] [--eid-field EID_FIELD] [--version] [-v {0,1,2,3}] [--settings SETTINGS] [--pythonpath PYTHONPATH] [--traceback]
                              [--no-color] [--force-color] [--skip-checks]
                              point_layer

    Load a layer with point geometries in the Dive model

    positional arguments:
      point_layer

    optional arguments:
      -h, --help            show this help message and exit
      --encoding ENCODING, -e ENCODING
                            File encoding, default utf-8
      --name-field NAME_FIELD, -n NAME_FIELD
      --depth-field DEPTH_FIELD, -d DEPTH_FIELD
      --practice-default PRACTICE_DEFAULT
      --structure-default STRUCTURE_DEFAULT
      --eid-field EID_FIELD
                            External ID field
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



Import Signage
--------------


``sudo geotrek help loadsignage``

::

    usage: manage.py loadsignage [-h] [--use-structure] [--encoding ENCODING] [--name-field NAME_FIELD] [--type-field TYPE_FIELD] [--condition-field CONDITION_FIELD]
                                 [--structure-field STRUCTURE_FIELD] [--description-field DESCRIPTION_FIELD] [--year-field YEAR_FIELD] [--code-field CODE_FIELD]
                                 [--type-default TYPE_DEFAULT] [--name-default NAME_DEFAULT] [--condition-default CONDITION_DEFAULT] [--structure-default STRUCTURE_DEFAULT]
                                 [--description-default DESCRIPTION_DEFAULT] [--eid-field EID_FIELD] [--year-default YEAR_DEFAULT] [--code-default CODE_DEFAULT] [--version]
                                 [-v {0,1,2,3}] [--settings SETTINGS] [--pythonpath PYTHONPATH] [--traceback] [--no-color] [--force-color] [--skip-checks]
                                 point_layer

    Load a layer with point geometries in te structure model

    positional arguments:
      point_layer

    optional arguments:
      -h, --help            show this help message and exit
      --use-structure       Allow to use structure for condition and type of infrastructures
      --encoding ENCODING, -e ENCODING
                            File encoding, default utf-8
      --name-field NAME_FIELD, -n NAME_FIELD
                            Name of the field that will be mapped to the Name field in Geotrek
      --type-field TYPE_FIELD, -t TYPE_FIELD
                            Name of the field that will be mapped to the Type field in Geotrek
      --condition-field CONDITION_FIELD, -c CONDITION_FIELD
                            Name of the field that will be mapped to the Condition field in Geotrek
      --structure-field STRUCTURE_FIELD, -s STRUCTURE_FIELD
                            Name of the field that will be mapped to the Structure field in Geotrek
      --description-field DESCRIPTION_FIELD, -d DESCRIPTION_FIELD
                            Name of the field that will be mapped to the Description field in Geotrek
      --year-field YEAR_FIELD, -y YEAR_FIELD
                            Name of the field that will be mapped to the Year field in Geotrek
      --code-field CODE_FIELD
                            Name of the field that will be mapped to the Code field in Geotrek
      --type-default TYPE_DEFAULT
                            Default value for Type field
      --name-default NAME_DEFAULT
                            Default value for Name field
      --condition-default CONDITION_DEFAULT
                            Default value for Condition field
      --structure-default STRUCTURE_DEFAULT
                            Default value for Structure field
      --description-default DESCRIPTION_DEFAULT
                            Default value for Description field
      --eid-field EID_FIELD
                            External ID field
      --year-default YEAR_DEFAULT
                            Default value for Year field
      --code-default CODE_DEFAULT
                            Default value for Code field
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


Import Cities
-------------


``sudo geotrek help loadcities``

::

    usage: manage.py loadcities [-h] [--code-attribute CODE] [--name-attribute NAME] [--encoding ENCODING] [--srid SRID] [--intersect] [--version] [-v {0,1,2,3}] [--settings SETTINGS]
                            [--pythonpath PYTHONPATH] [--traceback] [--no-color] [--force-color] [--skip-checks]
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


Import Districts
----------------


``sudo geotrek help loaddistricts``


::

    usage: manage.py loaddistricts [-h] [--name-attribute NAME] [--encoding ENCODING] [--srid SRID] [--intersect] [--version] [-v {0,1,2,3}] [--settings SETTINGS]
                                   [--pythonpath PYTHONPATH] [--traceback] [--no-color] [--force-color] [--skip-checks]
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



Import Restricted areas
-----------------------


``sudo geotrek help loadrestrictedareas``

::

    usage: manage.py loadrestrictedareas [-h] [--name-attribute NAME] [--encoding ENCODING] [--srid SRID] [--intersect] [--version] [-v {0,1,2,3}] [--settings SETTINGS]
                                         [--pythonpath PYTHONPATH] [--traceback] [--no-color] [--force-color] [--skip-checks]
                                         file_path area_type

    Load Restricted Area from a file within the spatial extent

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


Exploitation commands
=====================

Delete attachment from disk
---------------------------

When an attachment (eg. pictures) is removed, its file is not automatically removed from disk.
You have to run ``sudo geotrek clean_attachments`` manually or in a cron to remove old files.
After that, you should run ``sudo geotrek thumbnail_cleanup`` to remove old thumbnails.


Remove duplicate paths
----------------------

Duplicate paths can appear while adding paths with commands or directly in the application.
Duplicate paths can cause some problems of routing for topologies, it can generate corrupted topologies (that become MultiLineStrings instead of LineStrings).

You have to run ``sudo geotrek remove_duplicate_paths``

During the process of the command, every topology on a duplicate path will be set on the original path, and the duplicate path will be deleted.


Unset structure on categories
-----------------------------

Use this command if you wish to undo linking categories to structures for some models.


You have to run ``sudo geotrek unset_structure``

::

    usage: manage.py unset_structure [-h] [--all] [--list] [--version] [-v {0,1,2,3}] [--settings SETTINGS] [--pythonpath PYTHONPATH] [--traceback] [--no-color] [--force-color]
                                 [--skip-checks]
                                 [model [model ...]]

    Unset structure in lists of choices and group choices with the same name.

    positional arguments:
      model                 List of choices to manage

    optional arguments:
      -h, --help            show this help message and exit
      --all                 Manage all models
      --list                Show available models to manage
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

.. danger::
    You can't chose for each choice which set of category you want to unset structures, it will happen for all categories


Firstly, if a categroy is linked to a structure, it creates the same category but with no structure associated.
Secondly, every element with this old category gets assigned to this new category.
Finally all old categories are removed.



Reorder topologies
------------------

All topologies have information about which path they go through on and in which order.
Actually, when a path is split in 2 by another path, a new path is added to the database.
We need to add information for all topologies that need to go through this new path.
This is badly managed at the moment, especially for the order of passage of the paths.
``sudo geotrek reorder_topologies``

It removes a lot of useless information which can accelerate the process of editing topologies afterward.


During the process of this command, it tries to find a good order of passage on the paths which creates
only one Linestring from start to end. It stays as close as possible to the corrupted order. This command uses the same algorithm to generate one Linestring
when the order is not well managed during topologies' display.

.. danger::
    It can happens that this algorithm can't find any solution and will genereate a MultiLineString.
    This will be displayed at the end of the reorder



Automatication commands
-----------------------


You can set up automatic commands by creating a `cron` file under ``/etc/cron.d/geotrek_command`` that contains:

::

    0 3 * * * root /usr/sbin/geotrek <command> <options>

example :

::

    0 4 * * * root /usr/sbin/geotrek reorder_topologies


This example will automatically reorder topologies at 4 am every day.
