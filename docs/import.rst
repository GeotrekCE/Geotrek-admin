===============
IMPORT FROM SIT
===============


Configure APIDAE (ex-SITRA) import
----------------------------------

To import touristic content from APIDAE (ex-SITRA), create a ``bulkimport/parsers.py`` file with the following content:

::

    # -*- coding: utf8 -*-

    from geotrek.tourism.parsers import TouristicContentSitraParser

    class HebergementParser(TouristicContentSitraParser):
        label = u"Hébergements"
        api_key = 'xxxxxxxx'
        project_id = 9999
        selection_id = 99999
        category = u"Hébergement"
        type1 = [u"Camping"]
        type2 = [u"3 étoiles", "Tourisme et Handicap"]  # just remove this line if no type2

Then set up appropriate values:

* ``label`` at your convenience,
* ``api_key``, ``project_id`` and ``selection_id`` according to your APIDAE (ex-SITRA) configuration,
* ``category``, ``type1`` and ``type2`` to select in which Geotrek category/type imported objects should go (types are optional),
* rename the class ``HebergementParser`` if need be.

You can duplicate the class. Each class must have a different name.
Don't forget the u character before strings if they contain non-ascii characters.

To apply changes, you may have to run ``sudo supervisorctl restart all``.

Configure Marque Esprit Parc import
-----------------------------------

To import touristic content from Esprit Parc national database, create (or update) ``bulkimport/parsers.py`` file with the following content:

::

    # -*- coding: utf8 -*-

    from geotrek.tourism.parsers import EspritParcParser

    class XXXEspritParcParser(EspritParcParser):
        label = u"Marque Esprit Parc"
        url = u"http://gestion.espritparcnational.com/ws/?f=getProduitsSelonParc&codeParc=XXX"

Then set up appropriate values:

* ``XXX`` by unique national park code (ex: PNE)

You can duplicate the class. Each class must have a different name.
Don't forget the u character before strings if they contain non-ascii characters.

In this case categories and types in Geotrek database have to be the same as in Esprit parc database. Otherwise missing categories and types will be created in Geotrek database.

Imported contents will be automatically published and approved. 

If you use an url that filters a unique category, you can change its name. Example to get only Honey products and set the Geotrek category and type in which import them:

::

    class MielEspritParcParser(EspritParcParser):
        label = u"Miel Esprit Parc national"
        url = u"http://gestion.espritparcnational.com/ws/?f=getProduitsSelonParc&codeParc=XXX&typologie=API"
        constant_fields = {
            'category': u"GeotrekCategoryName",
            'published': True,
            'approved': True,
            'deleted': False,
        }
        m2m_constant_fields = {
            'type1': [u"GeotrekTypeName"],
        }

URL to get Esprit parc types: `http://gestion.espritparcnational.com/ws/?f=getTypologieProduits`.

Start import from command line
------------------------------

Just run:

::

    ./bin/django import bulkimport.parsers.HebergementParser

Change the last element ``HebergementParser`` to match one of the class names in ``bulkimport/parsers.py`` file.
You can add ``-v2`` parameter to make the command more verbose (show progress).
Thank to ``cron`` utility you can configure automatic imports.


Start import from Geotrek-Admin UI
----------------------------------

Open the top right menu and clic on ``imports``.
