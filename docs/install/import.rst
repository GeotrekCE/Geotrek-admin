===========
Import data
===========


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
* You can add ``delete = True`` in your class if you want to delete objects in Geotrek databases that has been deleted in your Apidae selection. It will only delete objects that match with your class settings (category, types, portal...)
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

Multiples import
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

Import from a file
------------------

You can also use some of Geotrek commands to import data from a vector file handled by GDAL (https://gdal.org/drivers/vector/index.htm) (e.g.: ESRI Shapefile, GeoJSON, GeoPackage etc.)

Possible data are e.g.: POI, infrastructures, signages, cities, districts, restricted areas.

You must use these commands to import spatial data because of the dynamic segmentation, which will not be computed if you enter the data manually. 

Here are the Geotrek commands available:

- ``loadinfrastructure``
- ``loadsignage``
- ``loadpoi``
- ``loadcities``
- ``loaddistricts``
- ``loadrestrictedareas``

Usually, these commands come with ability to match file attributes to model fields.
    
To get help about a command:

::

    sudo geotrek help <subcommand>
    
Example: ``sudo geotrek help loadpoi``

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


Delete attachment from disk
---------------------------

When an attachment (eg. pictures) is removed, its file is not automatically removed from disk.
You have to run ``sudo geotrek clean_attachments`` manually or in a cron to remove old files.
After that, you should run ``sudo geotrek thumbnail_cleanup`` to remove old thumbnails.
