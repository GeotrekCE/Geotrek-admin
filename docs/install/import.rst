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

You can also use some of Geotrek commands to import data from a file.

Possible data are e.g.: POI, infrastructures, signages, cities, districts, restricted areas.

You must use these commands to import spatial data because of the dynamic segmentation, which will not be computed if you enter the data manually. 

To list all Geotrek commands available:

::

    sudo geotrek
    
To get help about a command:

::

    sudo geotrek help <subcommand>
    
Example: ``sudo geotrek help loadpoi``

Delete attachment from disk
---------------------------

When an attachment (eg. pictures) is removed, its file is not automatically removed from disk.
You have to run `sudo geotrek clean_attachments` manually or in a cron to remove old files.
After that, you should run `sudo geotrek thumbnail_cleanup` to remove old thumbnails.
