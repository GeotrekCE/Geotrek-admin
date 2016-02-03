===============
IMPORT FROM SIT
===============


Configure SITRA import
----------------------

To import touristic content from SITRA, create a ``bulkimport/parsers.py`` file with the following content:

::

    # -*- coding: utf8 -*-

    from geotrek.tourism.parsers import TouristicContentSitraParser

    class HebergementParser(TouristicContentSitraParser):
        label = u"Hébergements"
        api_key = 'xxxxxxxx'
        project_id = 9999
        selection_id = 99999
        category = u"Hébergement"
        type1 = u""
        type2 = u""

Then set up appropriate values:

* ``label`` at your convenience,
* ``api_key``, ``project_id`` and ``selection_id`` according to your SITRA configuration,
* ``category``, ``type1`` and ``type2`` to select in which Geotrek category/type imported objects should go (types are optional),
* rename the class ``HebergementParser`` if need be.

You can duplicate the class. Each class must have a different name.
Don't forget the u character before strings if they contain non-ascii characters.

Configure Marque Esprit Parc import
-----------------------------------

To import touristic content from national park database, create (or update) ``bulkimport/parsers.py`` file with the following content:

::

    # -*- coding: utf8 -*-

    from geotrek.tourism.parsers import EspritParcParser

    class XXXEspritParcParser(EspritParcParser):
        label = u"Marque Esprit Parc"
        url = u"http://gestion.espritparcnational.com/ws/?f=getProduitsSelonParc&codeParc=XXX"
        LIMIT_CATEGORIES = ()
        LIMIT_TYPES = ()

Then set up appropriate values:

* ``XXX`` by unique national park code (ex: PNE)
* ``LIMIT_CATEGORIES`` by a list separated by commas (ex: (u"Sorties de découverte",) )
* ``LIMIT_TYPES`` by unique national park code (ex: (u"Randonnées pédestres",) )

You can duplicate the class. Each class must have a different name.
Don't forget the u character before strings if they contain non-ascii characters.


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
