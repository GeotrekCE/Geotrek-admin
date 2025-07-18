.. _import-from-touristic-data-systems:

=======================
Touristic Data Systems
=======================

.. abstract:: Keywords

   ``SIT``, ``parser``, ``command line``, ``import en ligne de commande``


Real-time integration
======================

Geotrek-admin integrates with various Tourism Information Systems (SIT) such as Apidae, Tourinsoft, and others, enabling real-time retrieval of data entered by tourism offices. This includes information on points of interest, accommodations, cultural heritage, and more.

These imported data elements are automatically linked to nearby treks, regardless of activity type (trekking, trail running, mountain biking, cycling, gravel, climbing, rafting, etc.).

This seamless integration enriches the descriptive pages of routes, ensuring that users benefit from comprehensive and up-to-date information with no additional effort required from administrators or agents.

.. _generic-settings-for-your-parser:

Generic settings for your parser
=================================

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
- ``flexible_fields`` if ``True``, external source fields are flexible, meaning no error is thrown if a mapped field is missing in the API response (default: ``False``)
- ``fields`` (default: ``None``)
- ``m2m_fields``  (default: ``{}``)
- ``constant_fields`` (default: ``{}``)
- ``m2m_constant_fields`` (default: ``{}``)
- ``m2m_aggregate_fields`` (default: ``[]``)
- ``non_fields`` (default: ``{}``)
- ``natural_keys`` (default: ``{}``)
- ``field_options`` (default: ``{}``)
- ``default_language`` use another default language for this parser (default: ``None``)
- ``default_fields_values`` sets default values for fields (default: ``{}``)

.. _start-import-from-command-line:

Start import from command line
===============================

Just run:

.. md-tab-set::
    :name: import-from-hebergement-parser-tabs

    .. md-tab-item:: With Debian

         .. code-block:: python

          sudo geotrek import HebergementParser

    .. md-tab-item:: With Docker

         .. code-block:: python

          docker compose run --rm web ./manage.py import  HebergementParser

Change ``HebergementParser`` to match one of the class names in ``var/conf/parsers.py`` file.
You can add ``-v2`` parameter to make the command more verbose (show progress).
Thank to ``cron`` utility you can configure automatic imports.

.. _start-import-from-geotrek-admin-ui:

Start import from Geotrek-admin UI
===================================

Open the top right menu and clic on ``imports``.

.. _import-from-apidae:

Import from APIDAE
====================

Import touristic content
------------------------

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
* See the `geotrek/tourism/parsers.py/ <https://github.com/GeotrekCE/Geotrek-admin/blob/master/geotrek/tourism/parsers.py/>`_  file for details about parsers

You can duplicate the class. Each class must have a different name.

To apply changes, you may have to run ``sudo service geotrek restart``.

Import treks
------------

A parser implementation is available to import Treks from APIDAE. Use it by defining a subclass of ``geotrek.trekking.parsers.ApidaeTrekParser`` in your ``var/conf/parsers.py`` configuration file as shown above.

You'll have to configure how to access your APIDAE data: ``api_key``, ``project_id`` and ``selection_id`` (those are setting attributes from the APIDAE base parser).

The ``practices_mapped_with_activities_ids`` and ``practices_mapped_with_default_activities_ids`` attributes define default mapping with the trekking module data fixture. You may override this to match your own types of Trek Practice.

Example of a parser configuration :

::

    class ImportTreksApidae(ApidaeTrekParser):
        label = "Import trek with eid"
        label_fr = "Import itinéraires avec identifiant externe"
        label_en = "Import trek with eid"
        eid = 'eid'

Import services
---------------

To import services from APIDAE, define a subclass of ``geotrek.trekking.parsers.ApidaeServiceParser`` in your ``var/conf/parsers.py`` configuration file.

In addition to the usual attributes, the service type name (``type``) must be specified. This type will be assigned to all objects imported through the parser.

Example of an APIDAE service parser configuration:

::

    class DrinkingWaterPoint(ApidaeServiceParser):
        label = "Drinking water points"
        provider = "Apidae"
        selection_id = 12345
        type = "Drinking water point"

.. _import-from-tourinsoft:

Import from Tourinsoft
======================

Tourinsoft is a Tourism Information System developed by the company Ingénie for tourism organizations in France, such as Departmental Tourism Committees (CDT), Tourism Development Agencies (ADT), and Tourist Offices. This system allows for the centralization, management, and standardized dissemination of tourism-related information.

Example of a parser configuration :

::

    class RestaurationParser(TouristicContentTourinsoftParser):
        """Restauration parsers"""
        label = "Restauration"
        category = "Restauration"
        url = "<Touristic content data feed URL"  # In the form https://api-v3.tourinsoft.com/api/syndications/decibelles-data.tourinsoft.com/<id>?format=json"

.. _import-from-cirkwi:

Import from Cirkwi
===================

The functionality for importing treks and touristic content from Cirkwi was developed and integrated into `version 2.111.0 of Geotrek-admin <https://github.com/GeotrekCE/Geotrek-admin/releases/tag/2.111.0/>`_.

.. note ::

    - By default, imported content is automatically published.
    - To enable the integration of this data, you need to modify the `parsers.py` file to create a dedicated parser and query a feed provided by Cirkwi.

The following parsers have been developed to facilitate data import from Cirkwi into Geotrek-admin:

- **Trek Parser**: Allows the integration of treks from Cirkwi into Geotrek. This parser is compatible with instances operating in :ref:`Non-Dynamic Segmentation <configuration-dynamic-segmentation>` (NDS) mode only.

Example of a parser configuration :

::

    class ImportTreksCirkwi(CirkwiTrekParser):
        url = "<Treks data feed URL>"  # In the form https://ws.cirkwi.com/flux/<user>/<code>/circuits.php?widget-id=<id>
        user = "<Username>"
        password = "<Password>"
        auth = (user, password)
        label = "Cirkwi's treks"
        delete = True
        create = True
        provider = "Cirkwi"


- **Touristic content Parser**: Enables the import of touristic content from Cirkwi into Geotrek.

Example of a parser configuration :

::

    class ImportTouristicContentCirkwi(CirkwiTouristicContentParser):
        url = "<Treks data feed URL>"  # In the form https://ws.cirkwi.com/flux/<user>/<code>/circuits.php?widget-id=<id>"
        user = "<Username>"
        password = "<Password>"
        auth = (user, password)
        label = "Cirkwi's touristic content"
        delete = True
        create = True
        provider = "Cirkwi"
        # results_path = "circuit/pois/poi"  # Uncomment this line if the touristic content to be imported come from the same feed as  treks

.. seealso::

  To import Geotrek treks and POIs into Cirkwi's format you can check :ref:`this section (french)  <geotrek-ignrando-cirkwi-api>`.

.. _import-from-lei:

Import from LEI
================

To import touristic content or touristic event from LEI , create (or update) ``/opt/geotrek-admin/var/conf/parsers.py`` file with the following content:

::

    from geotrek.tourism.parsers import LEITouristicContentParser, LEITouristicEventParser

    class XXXLEIContentParser(LEITouristicContentParser):
        label = "LEI TouristicContent"
        url = "https://url.asp"

    class XXXLEIEventParser(LEITouristicEventParser):
        label = "LEI TouristicEvent"
        url = "https://url.asp"

.. _import-from-marque-esprit-parc:

Import from Marque Esprit Parc
===============================

To import touristic content from Esprit Parc national database, create (or update) ``/opt/geotrek-admin/var/conf/parsers.py`` file with the following content:

::

    from geotrek.tourism.parsers import EspritParcParser

    class XXXEspritParcParser(EspritParcParser):
        label = "Marque Esprit Parc"
        url = "https://gestion.espritparcnational.com/ws/?f=getProduitsSelonParc&codeParc=XXX"

Then set up appropriate values:

* ``XXX`` by unique national park code (ex: PNE)

You can duplicate the class. Each class must have a different name.

In this case categories and types in Geotrek database have to be the same as in Esprit parc database. Otherwise missing categories and types will be created in Geotrek database.

Imported contents will be automatically published and approved (certified).

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

.. _import-from-openstreetmap:

Import from OpenStreetMap
==========================

OpenStreetMap (OSM) is a collaborative, open-source mapping database that provides freely accessible geographic data, maintained by a global community of contributors. OpenStreetMap parsers retrieve OSM data using the `Overpass API <https://wiki.openstreetmap.org/wiki/Overpass_API>`_.

By default, the parser uses the German Overpass server:
``https://overpass-api.de/api/interpreter/``.

You can override this by setting a custom URL in the ``url`` attribute of the ``OpenStreetMapParser`` class.

Query configuration
-------------------

Overpass queries are written in `Overpass QL <https://wiki.openstreetmap.org/wiki/Overpass_API/Overpass_QL>`_. Query configuration is handled through the ``query_settings`` attribute, which includes:

* ``bbox_margin`` (default: ``0.0``): A proportional buffer applied to the query bounding box. It expands the area by a fraction of its width to ensure surrounding features are included. (exemple: if bbox_margin is 0.05 then the bbox will be expanded by 5%)

* ``osm_element_type`` (default: ``nwr``): Specifies the types of elements to retrieve: ``"node"``, ``"way"``, ``"relation"``, or ``"nwr"`` (all three).

* ``output`` (default: ``"geom"``): Specifies the data returned by the Overpass API.
    * ``geom``: return the object type, the object ID, the tags and the geometry
    * ``tags``: return the object type, the object ID and the tags

The ``tags`` attribute defines the set of tag filters to be used with the Overpass API.
It is a list where each element is either:

* A **dictionary**: representing a single tag filter (e.g., ``{"highway": "bus_stop"}``)

* A **list of dictionaries**: representing a logical AND across all contained tags
            (e.g., [{"boundary": "administrative"}, {"admin_level": "4"}] means the object must have both tags).

The Overpass query will return the UNION of all top-level items.

For example:

::

    self.tags = [
        [{"boundary": "administrative"}, {"admin_level": "4"}],
        {"highway": "bus_stop"}
    ]

*means*: return objects that either have both ``boundary=administrative`` AND ``admin_level=4``, OR have ``highway=bus_stop``.

All the objects parsed by the ``OpenStreetMap`` parsers will be those contained in the ``settings.SPATIAL_EXTENT`` bounding box.
You can change the bounding box by overriding ``get_bbox_str()``.

Handling translated fields
--------------------------

OpenStreetMap supports multilingual fields using tags like ``name:fr``, following the ISO 639-1 standard.

During import, the parser maps translated fields (e.g., ``name``, ``description``) based on the model and the languages defined in ``settings.MODELTRANSLATION_LANGUAGES``. For each language, it creates a mapping such as ``name_fr`` → ``name:fr``.

For the default language (``settings.MODELTRANSLATION_DEFAULT_LANGUAGE``), a special mapping is applied: it includes a fallback to the base tag (e.g., ``name``) and maps it to the base Geotrek field name (e.g., ``name``). This allows for filtering operations without relying directly on the default language code.

If a translation is missing, the field remains unset unless a fallback value is provided in ``default_fields_values`` using the pattern ``{field}_{lang}``.

When no translation exists for the default language, the base OpenStreetMap tag (e.g., ``name``) is used. This can lead to incorrect language display if the OSM default does not match the Geotrek instance’s default language.

Translation logic can be customized in custom parsers by overriding the ``translation_fields`` method.

Attachments
-----------
``OpenStreetMapParser`` automatically attaches files from ``wikimedia_commons`` and ``image`` tags found in the data.
A ``CC BY-SA 4.0`` license is assigned to each imported file, as specified by the OpenStreetMap license.

For more information on how attachments work, consult :ref:`this section <import-attachments>`.

.. _import-information-desk:

Import information desks
------------------------

To import information desks from OpenStreetMap, edit the ``var/conf/parsers.py`` file with the following content:

::

    from geotrek.tourism.parsers import InformationDeskOpenStreetMapParser

    class MaisonDuParcParser(InformationDeskOpenStreetMapParser):
        provider = "OpenStreetMap"
        tags = [{"amenity": "ranger_station"}]
        default_fields_values = {"name": "Maison du Parc"}
        type = "Maisons du parc"

Then set up appropriate values:

* ``tags`` to filter the objects imported from OpenStreetMap (see `MapFeatures <https://wiki.openstreetmap.org/wiki/Map_features/>`_  to get a list of existing tags)
* ``default_fields_values`` to define a value that will be assigned to a specific field when the external object does not contain the corresponding tag
* ``type`` to specify the Geotrek type for imported objects
* See the `geotrek/tourism/parsers.py/ <https://github.com/GeotrekCE/Geotrek-admin/blob/master/geotrek/tourism/parsers.py/>`_  file for details about parsers

You can duplicate the class to import different types of information desks. In that case, each class must have a unique name and provider label.

.. _import-touristic-contents:

Import touristic contents
-------------------------

To import touristic content from OpenStreetMap, edit the ``var/conf/parsers.py`` file with the following content:

::

    from geotrek.tourism.parsers import OpenStreetMapTouristicContentParser

    class RestaurantParser(OpenStreetMapTouristicContentParser):
        provider = "OpenStreetMap"
        tags = [{"amenity": "restaurant"}]
        default_fields_values = {"name": "restaurant"}
        category = "Restaurants"
        type1 = "Restaurant"

Then set up appropriate values:

* ``tags`` to filter the objects imported from OpenStreetMap (see `MapFeatures <https://wiki.openstreetmap.org/wiki/Map_features/>`_  to get a list of existing tags)
* ``default_fields_values`` to define a value that will be assigned to a specific field when the external object does not contain the corresponding tag
* ``category`` (mandatory), ``type1`` and ``type2`` (optional) to select in which Geotrek category/type imported objects should go. ``type1`` and ``type2`` can have multiple values (ex: ``type1 = ["Restaurant", "Hotel"]``)
* ``portal`` to select in which portal(s) the objects should appear. Multiple portals can be assigned (ex: ``portal = ["portal 1", "portal 2"]``)
* ``source`` to select the data source. Multiple sources can be assigned (ex: ``source = ["source 1", "source 2"]``)
* ``themes`` to select the corresponding theme(s) of the parsed objects. Multiple themes can be assigned (ex: ``themes = ["theme 1", "theme 2"]``)
* See the `geotrek/tourism/parsers.py/ <https://github.com/GeotrekCE/Geotrek-admin/blob/master/geotrek/tourism/parsers.py/>`_  file for details about parsers


.. _import-poi:

Import points of interest (POIs)
--------------------------------

To import point of interest (POI) from OpenStreetMap, edit the ``var/conf/parsers.py`` file with the following content:

::

    from geotrek.trekking.parsers import OpenStreetMapPOIParser

    class HistoryParser(OpenStreetMapPOIParser):
        provider = "OpenStreetMap"
        tags = [
            {"historic": "yes"},
            {"historic": "castel"},
            {"historic": "memorial"},
            {"historic": "fort"},
            {"historic": "bunker"},
            {"building": "chapel"},
            {"building": "bunker"},
        ]
        default_fields_values = {"name": "Historic spot"}
        type = "Histoire"

Then set up appropriate values:

* ``tags`` to filter the objects imported from OpenStreetMap (see `MapFeatures <https://wiki.openstreetmap.org/wiki/Map_features/>`_  to get a list of existing tags)
* ``default_fields_values`` to define a value that will be assigned to a specific field when the external object does not contain the corresponding tag
* ``type`` to specify the Geotrek type for imported objects
* See the `geotrek/trekking/parsers.py/ <https://github.com/GeotrekCE/Geotrek-admin/blob/master/geotrek/trekking/parsers.py/>`_  file for details about parsers

The parsed objects will be those contained in the ``settings.SPATIAL_EXTENT`` bounding box.
You can duplicate the class to import different types of points of interest. In that case, each class must have a unique name and provider label.

.. _import-cities-osm :

Import cities
-----------------

To import cities from OpenStreetMap, edit the ``var/conf/parsers.py`` file with the following content:

::

    from geotrek.zoning.parsers import OpenStreetMapCityParser

    class CityParser(OpenStreetMapCitiesParser):
        provider = "OpenStreetMap"
        tags = [
            [{"boundary": "administrative"}, {"admin_level": "8"}],
        ]
        default_fields_values = {"name": "city"}
        code_tag = "ref:INSEE"

Then set up appropriate values:

* ``tags`` to filter the objects imported from OpenStreetMap (see `MapFeatures <https://wiki.openstreetmap.org/wiki/Map_features/>`_  to get a list of existing tags)
* ``default_fields_values`` to define a value that will be assigned to a specific field when the external object does not contain the corresponding tag
* ``code_tag`` to specify the OpenStreetMap tag that contains the code information (e.g., in France, code_tag = "ref:INSEE"). If no value is defined, the code will not be included.
* See the `geotrek/zoning/parsers.py/ <https://github.com/GeotrekCE/Geotrek-admin/blob/master/geotrek/zoning/parsers.py/>`_  file for details about parsers

The parsed objects will be those contained in the ``settings.SPATIAL_EXTENT`` bounding box.


.. _import-district:

Import districts
-----------------

To import districts from OpenStreetMap, edit the ``var/conf/parsers.py`` file with the following content:

::

    from geotrek.zoning.parsers import OpenStreetMapDistrictParser

    class DistrictParser(OpenStreetMapDistrictParser):
        provider = "OpenStreetMap"
        tags = [
            [{"boundary": "administrative"}, {"admin_level": "6"}], # departement
            [{"boundary": "administrative"}, {"admin_level": "4"}], # region
        ]
        default_fields_values = {"name": "district"}

Then set up appropriate values:

* ``tags`` to filter the objects imported from OpenStreetMap (see `MapFeatures <https://wiki.openstreetmap.org/wiki/Map_features/>`_  to get a list of existing tags)
* ``default_fields_values`` to define a value that will be assigned to a specific field when the external object does not contain the corresponding tag
* See the `geotrek/zoning/parsers.py/ <https://github.com/GeotrekCE/Geotrek-admin/blob/master/geotrek/zoning/parsers.py/>`_  file for details about parsers

The parsed objects will be those contained in the ``settings.SPATIAL_EXTENT`` bounding box.

.. _import-restricted-area:

Import restricted areas
-----------------------

To import restricted areas from OpenStreetMap, edit the ``var/conf/parsers.py`` file with the following content:

::

    from geotrek.zoning.parsers import OpenStreetMapRestrictedAreaParser

    class RegionalNatureParkParser(OpenStreetMapDistrictParser):
        provider = "OpenStreetMap"
        tags = [{"protection_title"="parc naturel régional"}]
        default_fields_values = {"name": "parc naturel régional"}
        area_type = "Inconnu"

Then set up appropriate values:

* ``tags`` to filter the objects imported from OpenStreetMap (see `MapFeatures <https://wiki.openstreetmap.org/wiki/Map_features/>`_  to get a list of existing tags)
* ``default_fields_values`` to define a value that will be assigned to a specific field when the external object does not contain the corresponding tag
* ``area_type`` to specify the restricted area type for imported objects
* See the `geotrek/zoning/parsers.py/ <https://github.com/GeotrekCE/Geotrek-admin/blob/master/geotrek/zoning/parsers.py/>`_  file for details about parsers

the parsed objects will be those that intersect the ``settings.SPATIAL_EXTENT`` bounding box.

.. _import-signage-osm:

Import signages
---------------

To import signage from OpenStreetMap, edit the ``var/conf/parsers.py`` file with the following content:

::

    from geotrek.signage.parsers import OpenStreetMapSignageParser

    class DirectionalParser(OpenStreetMapSignageParser):
        provider = "OpenStreetMap"
        tags = [{"information": "guidepost"}]
        default_fields_values = {"name": "guidepost"}
        type = "Directionelle"

Then set up appropriate values:

* ``tags`` to filter the objects imported from OpenStreetMap (see `MapFeatures <https://wiki.openstreetmap.org/wiki/Map_features/>`_  to get a list of existing tags)
* ``default_fields_values`` to define a value that will be assigned to a specific field when the external object does not contain the corresponding tag
* ``type`` to specify the Geotrek type for imported objects
* See the `geotrek/signage/parsers.py/ <https://github.com/GeotrekCE/Geotrek-admin/blob/master/geotrek/signage/parsers.py/>`_  file for details about parsers

.. _import-infrastructures_osm:

Import Infrastructures
----------------------

To import infrastructures from OpenStreetMap, edit the ``var/conf/parsers.py`` file with the following content:

::

    from geotrek.infrastructure.parsers import OpenStreetMapInfrastructureParser

    class TableParser(OpenStreetMapInfrastructureParser):
        provider = "OpenStreetMap"
        tags = [
            {"leisure": "picnic_table"},
            {"tourism": "picnic_table"}
        ]
        default_fields_values = {"name": "picnic table"}
        type = "Table"

Then set up appropriate values:

* ``tags`` to filter the objects imported from OpenStreetMap (see `MapFeatures <https://wiki.openstreetmap.org/wiki/Map_features/>`_  to get a list of existing tags)
* ``default_fields_values`` to define a value that will be assigned to a specific field when the external object does not contain the corresponding tag
* ``type`` to specify the Geotrek type for imported objects
* See the `geotrek/infrastructure/parsers.py/ <https://github.com/GeotrekCE/Geotrek-admin/blob/master/geotrek/infrastructure/parsers.py/>`_  file for details about parsers

You can duplicate the class to import different types of information desks. In that case, each class must have a unique name and provider label.

.. _import-outdoor-site-osm:

Import outdoor sites
--------------------

To import outdoor sites from OpenStreetMap, edit the ``var/conf/parsers.py`` file with the following content:

::

    from geotrek.outdoor.parsers import OpenStreetMapOutdoorSiteParser

    class ClimbingSiteParser(OpenStreetMapOutdoorSiteParser):
        provider = "OpenStreetMap"
        tags = [{"sports": "climbing"}]
        default_fields_values = {"name": "climbing site"}
        practice = "Escalade"

Then set up appropriate values:

* ``tags`` to filter the objects imported from OpenStreetMap (see `MapFeatures <https://wiki.openstreetmap.org/wiki/Map_features/>`_  to get a list of existing tags)
* ``default_fields_values`` to define a value that will be assigned to a specific field when the external object does not contain the corresponding tag
* ``practice`` to select in which Geotrek practice imported objects should go.
* ``portal`` to select in which portal(s) the objects should appear. Multiple portals can be affected (ex: portal = ["portal 1", "portal 2"])
* ``source`` to select the data source. Multiple sources can be affected (ex: source = ["source 1", "source 2"])
* ``themes`` to select the corresponding theme(s) of the parsed objects. Multiple themes can be affected (ex: themes = ["theme 1", "theme 2"])
* See the `geotrek/outdoor/parsers.py/ <https://github.com/GeotrekCE/Geotrek-admin/blob/master/geotrek/outdoor/parsers.py/>`_  file for details about parsers

.. _format_geometries:

Geometry filtering in Geotrek Parsers
======================================

In some cases, you may want to restrict imported objects to a specific geographic area already defined in geotrek model instance (ex: a City or District).
This can be done by defined the parser’s ``intersection_geom`` attribute

This attribute is a dictionary with the following keys:

- ``model``: The Django model containing the reference geometry object.
- ``app_label``: The Django application where the model is defined.
- ``geom_field``: The name of the geometry field in the model.
- ``object_filter``: A dictionary to identify the reference object (e.g., using an ID).

The ``object_filter`` must return exactly one object:

- If no object is found, the parser raises a **blocking error**.
- If multiple objects are returned, only the **first** will be used, which may cause unexpected behavior.

Conditional Deletion with ``delete = True``
-------------------------------------------

If ``delete`` attribut is set to ``True``, the parser will automatically **delete existing objects** of the current model
that **do not intersect** the reference geometry.

.. note::

   Deletion only affects objects of the model handled by the current parser. Other models are not impacted.

.. _import-attachments:

Import attachments
==================

``AttachmentParserMixin`` lets a parser **link (and optionally download) media files** to any object it imports (signage, infrastructures, POIs, touristic content, events, etc).
The mixin is located in ``geotrek/common/parsers.py`` and must be inherited by your parser:

.. code-block:: python

   class ExampleParser(AttachmentParserMixin, Parser):

       # Parser configuration …

.. warning::

   Use ``AttachmentParserMixin`` **only in base parsers**.
   Custom parsers should focus on configuration.
   Factor attachment logic into shared base classes to keep custom parsers clean and maintainable.

Attributes
----------

The following attributes can be customized:

* ``download_attachments`` (default: ``True``):
  Whether to download and store attachments via Paperclip. If set to ``False``, attachments are only linked.
  Requires ``PAPERCLIP_ENABLE_LINK = True`` in Django settings.

* ``base_url`` (default: ``""``):
  Base URL prepended to each relative attachment path returned by ``filter_attachments``.

* ``delete_attachments`` (default: ``True``):
  After the new attachments have been processed, **every existing
  attachment that is *not* present in the current feed (or whose file has
  been replaced)** is permanently removed.

* ``filetype_name`` (default: ``"Photographie"``):
  Label of the ``FileType`` model assigned to all imported files.
  If it does not exist in the database, the import will fail with a warning:

  ::

     FileType '<name>' does not exist in Geotrek-Admin. Please add it

* ``non_fields`` (default: ``{"attachments": _("Attachments")}``):
  Maps the internal ``attachments`` field to the field name(s) containing attachments data in the external source.

* ``default_license_label`` (default: ``None``):
  If specified, this license will be assigned to all imported attachments.
  If the license does not exist, it will be created automatically.

Filtering attachments
---------------------

The ``filter_attachments`` method formats the external source data to match with the internal format.

If the attachment data has a different structure than the default ``filter_attachments``, the method must be overridden.

See the `geotrek/common/parsers.py/ <https://github.com/GeotrekCE/Geotrek-admin/blob/master/geotrek/common/parsers.py/>`_ file to see more about attachments.

.. _multiple-imports:

Multiple imports
=================

When you need to import data for the same object found in 2 different parsers, you can to force the aggregation of both values in many to many relationship case.
It can be interesting with portals for example.

Parameters for the aggregation : ``m2m_aggregate_fields``

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


.. _importing-from-multiple-sources-with-deletion:

Importing from multiple sources with deletion
==============================================

When importing data for the same model using two (or more) different sources, the ``provider`` field should be used to differenciate between sources, allowing to enable object deletion with ``delete = True`` without causing the last parser to delete objects created by preceeding parsers.

In the following example, ``Provider_1Parser`` and ``Provider_2Parser`` will each import their objects, set the ``provider`` field on these objects, and only delete objects that disappeared from their respective source since last parsing.

.. code-block:: python

    class Provider_1Parser(XXXXParser):
        delete = True
        provider = "provider_1"

    class Provider_2Parser(XXXParser):
        delete = True
        provider = "provider_2"

.. important::

    - It is recommended to use ``provider`` from the first import.
    - Do not add a ``provider`` field to preexisting parsers that already imported objects, or you will have to manually set the same value for ``provider`` on all objects already created by this parser.
    - If a parser does not have a ``provider`` value, it will not take providers into account, meaning that it could delete objects from preceeding parsers even if these other parsers do have a ``provider`` themselves.

The following example would cause ``NoProviderParser`` to delete objects from ``Provider_2Parser`` and ``Provider_1Parser``.

.. code-block:: python

    class Provider_1Parser(XXXXParser):
        delete = True
        provider = "provider_1"

    class Provider_2Parser(XXXParser):
        delete = True
        provider = "provider_2"

    class NoProviderParser(XXXParser):
        delete = True
        provider = None # (default)

.. seealso::

  To set up automatic commands you can check the :ref:`Automatic commands section <automatic-commands>`.

Linking Source Objects via `eid`
================================

Starting with **Geotrek-admin 2.117.0**, the `eid` (external ID) field displayed on the object detail page can now include a clickable link to the original source object.

To enable this, a new database model called **Provider** has been added. This model can be managed through the Django admin interface and includes the following fields:

- **Name**
- **Link template** (an HTML snippet used to build the link using the `eid`)
- **Copyright**

The link template should contain the `{{object.eid}}` placeholder, which will be replaced by the actual external ID. For example:

.. code-block:: html

   <a href="https://example.com/objects/{{object.eid}}" target="_blank">{{object.eid}}</a>

Fixtures are available for two providers: **OpenStreetMap** and **Apidae**. These predefined Provider records can be loaded during a new installation.
See the :ref:`fixture documentation <load-fixtures>` to see more about fixtures.

.. note::

    These fixtures are intended for new installations only. When upgrading an existing system, Provider records will be created automatically based on the existing `provider` field in the database. After upgrading, you must manually fill in the link template and copyright.

    You can reuse the link templates provided in the fixture files, available here:
    `Provider fixtures on GitHub <https://github.com/GeotrekCE/Geotrek-admin/tree/master/geotrek/common/fixtures/basic.json#L242>`_