.. _development-parser-import:

======================
Development
======================

The Parser class
================

The ``Parser`` class defines the core parsing logic and serves as a base class for all concrete parsers, which must inherit from it.

.. _available-attributs:

Available attributes
----------------------

+-------------------------------+----------+------------------------------------------------------------------------------------------------------------------------------------------------------+
| **Parameter**                 | **Type** | **Description**                                                                                                                                      |
+-------------------------------+----------+------------------------------------------------------------------------------------------------------------------------------------------------------+
| label                         | str      | Display name shown in the interface to identify this parser.                                                                                         |
+-------------------------------+----------+------------------------------------------------------------------------------------------------------------------------------------------------------+
| model                         | str      | Name of the data model where the information should be saved.                                                                                        |
+-------------------------------+----------+------------------------------------------------------------------------------------------------------------------------------------------------------+
| filename                      | str      | Name of the source file containing the data to import.                                                                                               |
+-------------------------------+----------+------------------------------------------------------------------------------------------------------------------------------------------------------+
| url                           | str      | API address where the data comes from.                                                                                                               |
+-------------------------------+----------+------------------------------------------------------------------------------------------------------------------------------------------------------+
| simplify_tolerance            | float    | Minimum distance (in meters) between two points of a geographic shape. Points that are too close may be removed to simplify the shape.               |
+-------------------------------+----------+------------------------------------------------------------------------------------------------------------------------------------------------------+
| update_only                   | bool     | If enabled, only existing data can be updated. No new object will be created.                                                                        |
+-------------------------------+----------+------------------------------------------------------------------------------------------------------------------------------------------------------+
| delete                        | bool     | If enabled, objects no longer present in the new data will be deleted.                                                                               |
+-------------------------------+----------+------------------------------------------------------------------------------------------------------------------------------------------------------+
| duplicate_eid_allowed         | bool     | If enabled, multiple objects can have the same external identifier.                                                                                  |
+-------------------------------+----------+------------------------------------------------------------------------------------------------------------------------------------------------------+
| fill_empty_translated_fields  | bool     | Automatically fills in empty translation fields (e.g. ``name_fr`` and ``name_en`` for the ``name`` field).                                           |
+-------------------------------+----------+------------------------------------------------------------------------------------------------------------------------------------------------------+
| warn_on_missing_fields        | bool     | Shows a warning message if expected fields are missing from the imported data.                                                                       |
+-------------------------------+----------+------------------------------------------------------------------------------------------------------------------------------------------------------+
| warn_on_missing_objects       | bool     | Shows a warning message if expected objects are not found in the imported data.                                                                      |
+-------------------------------+----------+------------------------------------------------------------------------------------------------------------------------------------------------------+
| separator                     | str      | Character used to separate multiple values in a single cell (e.g., a comma).                                                                         |
+-------------------------------+----------+------------------------------------------------------------------------------------------------------------------------------------------------------+
| eid                           | str      | Name of the field that contains the unique external identifier for each object.                                                                      |
+-------------------------------+----------+------------------------------------------------------------------------------------------------------------------------------------------------------+
| provider                      | str      | Name of the source the data comes from (e.g., a partner or an API name).                                                                             |
+-------------------------------+----------+------------------------------------------------------------------------------------------------------------------------------------------------------+
| fields                        | dict     | Mapping between model fields and source fields. A model field can be linked to multiple source fields.                                               |
+-------------------------------+----------+------------------------------------------------------------------------------------------------------------------------------------------------------+
| constant_fields               | dict     | Assigns fixed values to specific model fields for every imported object.                                                                             |
+-------------------------------+----------+------------------------------------------------------------------------------------------------------------------------------------------------------+
| m2m_fields                    | dict     | Mapping between model's many-to-many fields and those from the source.                                                                               |
+-------------------------------+----------+------------------------------------------------------------------------------------------------------------------------------------------------------+
| m2m_constant_fields           | dict     | Fixed values to be assigned to many-to-many fields for each object.                                                                                  |
+-------------------------------+----------+------------------------------------------------------------------------------------------------------------------------------------------------------+
| m2m_aggregate_fields          | list     | List of many-to-many fields where new data should be added without removing existing data.                                                           |
+-------------------------------+----------+------------------------------------------------------------------------------------------------------------------------------------------------------+
| non_fields                    | dict     | Mapping of source data to fields not part of the main model (e.g., ancillary data).                                                                  |
+-------------------------------+----------+------------------------------------------------------------------------------------------------------------------------------------------------------+
| natural_keys                  | dict     | Indicates which field to use to identify related objects (e.g., for foreign key relationships).                                                      |
+-------------------------------+----------+------------------------------------------------------------------------------------------------------------------------------------------------------+
| field_options                 | dict     | Optional parameters to customize how each field is processed during import.                                                                          |
|                               |          |    * ``create``: Create the related object in a foreign model if it does not exist. *(ex: field_options={"source": {"create": True}})*               |
|                               |          |    * ``requiered``: Skip the current item if the field is missing in the source data. *(ex: field_options={"name": {"required": True}})*             |
|                               |          |    * ``mapping``: Replace the field value based on a static mapping dictionary. *(ex: field_options={"route": {"mapping": {"BOUCLE": "boucle"}}})*   |
+-------------------------------+----------+------------------------------------------------------------------------------------------------------------------------------------------------------+
| default_language              | str      | Default language used for imported data.                                                                                                             |
+-------------------------------+----------+------------------------------------------------------------------------------------------------------------------------------------------------------+
| intersection_geom             | dict     | Geographic area to restricts imported objects (e.g., a City or District).                                                                            |
+-------------------------------+----------+------------------------------------------------------------------------------------------------------------------------------------------------------+


.. _general-architecture:

Execution flow diagram
-----------------------

.. graphviz::

   digraph {
       PARSE    [label="PARSE\nstarts data import"]
       START    [label="START\nlists database objects"]
       NEXT_ROW [label="NEXT_ROW\niterates over input rows"]
       PARSE_ROW [label="PARSE_ROW\nhandles full row import"]
       END      [label="END\ndeletes outdated objects"]
       PARSE_OBJ [label="PARSE_OBJ\ncreates/updates object"]
       GET_EID_KWARGS [label="GET_EID_KWARGS\ngets unique ID"]
       PARSE_FIELDS [label="PARSE_FIELDS\nhandles all object fields"]
       PARSE_FIELD [label="PARSE_FIELD\nindividual field import"]
       GET_VAL  [label="GET_VAL\ngets field values"]
       PARSE_TRANSLATION_FIELD [label="PARSE_TRANSLATION_FIELD\nupdates translated field"]
       PARSE_REAL_FIELD [label="PARSE_REAL_FIELD\nupdates real field"]
       PARSE_NON_FIELD [label="PARSE_NON_FIELD\nhandles special fields"]
       GET_PART [label="GET_PART\nextract nested data"]
       SET_VALUE [label="SET_VALUE\nsave value"]
       APPLY_FILTER [label="APPLY_FILTER\nfilter fk/m2m"]

       PARSE -> START
       PARSE -> NEXT_ROW
       PARSE -> PARSE_ROW
       PARSE -> END
       PARSE_ROW -> PARSE_OBJ
       PARSE_ROW -> GET_EID_KWARGS
       PARSE_OBJ -> PARSE_FIELDS
       PARSE_FIELDS -> PARSE_FIELD
       PARSE_FIELD -> GET_VAL
       PARSE_FIELD -> PARSE_TRANSLATION_FIELD
       PARSE_FIELD -> PARSE_REAL_FIELD
       PARSE_FIELD -> PARSE_NON_FIELD
       GET_VAL -> GET_PART
       PARSE_TRANSLATION_FIELD -> SET_VALUE
       PARSE_REAL_FIELD -> SET_VALUE
       PARSE_REAL_FIELD -> APPLY_FILTER
   }

.. _configurable-built-in-parsers:

Configurable built-in parsers
=============================

.. _apidae-parsers:

APIDAE
------
`Apidae <https://www.apidae-tourisme.com/>`_ is a collaborative network and a tourism information management platform. It enables tourist offices, local authorities, service providers, and private partners to share, structure, and distribute tourism data (accommodations, events, sites, services, etc.). It serves as a common reference system at the local, regional, and national levels.

Configure APIDAE access
~~~~~~~~~~~~~~~~~~~~~~~
To access your APIDAE data, you must define the following attributes in your parser class (inherited from an APIDAE base parser):

* ``api_key``: Your personal API key provided by APIDAE
* ``project_id``: The ID of your APIDAE project
* ``selection_id``: The ID of the selection containing the data to import

These values are required and should be filled in according to your APIDAE (formerly SITRA) configuration.

.. md-tab-set::
    :name: importdata-apidae-tabs

    .. md-tab-item:: Touristic content

        To import touristic content from APIDAE (ex-SITRA), define a subclass of ``geotrek.tourism.parsers.TouristicContentApidaeParser`` in your ``var/conf/parsers.py`` file with the following content:

        ::

            class HebergementParser(TouristicContentApidaeParser):
                label = "Hébergements"
                api_key = 'xxxxxxxx'
                project_id = 9999
                selection_id = 99999
                category = "Hébergement"
                type1 = ["Camping"]
                type2 = ["3 étoiles", "Tourisme et Handicap"]  # just remove this line if no type2

        Then set up appropriate values:

        * ``label`` at your convenience
        * ``category``, ``type1`` and ``type2`` (optional) to select in which Geotrek category/type imported objects should go
        * You can add ``delete = True`` in your class if you want to delete objects in Geotrek databases that has been deleted in your Apidae selection. It will only delete objects that match with your class settings (category, types, portal, provider...)
        * You can also use the class ``HebergementParser`` if you only import accommodations
        * See the `geotrek/tourism/parsers.py <https://github.com/GeotrekCE/Geotrek-admin/blob/master/geotrek/tourism/parsers.py>`__ file for details about parsers

        You can duplicate the class. Each class must have a different name.

    .. md-tab-item:: Treks

        To import treks from APIDAE (ex-SITRA), define a subclass of ``geotrek.trekking.parsers.ApidaeTrekParser`` in your  ``var/conf/parsers.py`` file with the following content:

        ::

            class ImportTreksApidae(ApidaeTrekParser):
                label = "Import trek with eid"
                label_fr = "Import itinéraires avec identifiant externe"
                label_en = "Import trek with eid"
                api_key = 'xxxxxxxx'
                project_id = 9999
                selection_id = 99999
                eid = 'eid'
                practices_mapped_with_activities_ids = {
                    'Pratique Pédestre': [
                        3172,  # Itinéraire de randonnée pédestre
                    ],
                }
                practices_mapped_with_default_activities_ids = {
                    'Pratique Pédestre': 3184,  # Sports pédestres
                }

        Then set up appropriate values:

        * ``label`` at your convenience
        * ``practices_mapped_with_activities_ids`` and ``practices_mapped_with_default_activities_ids`` define default mapping with the trekking module data fixture
        * See the `geotrek/trekking/parsers.py <https://github.com/GeotrekCE/Geotrek-admin/blob/master/geotrek/trekking/parsers.py>`__ file for details about parsers

    .. md-tab-item:: Services

        To import services from APIDAE (ex-SITRA), define a subclass of ``geotrek.trekking.parsers.ApidaeServiceParser`` in your ``var/conf/parsers.py`` file with the following content:

        ::

            class DrinkingWaterPoint(ApidaeServiceParser):
                label = "Drinking water points"
                provider = "Apidae"
                selection_id = 12345
                service_type = "Drinking water point"

        Then set up appropriate values:

        * ``label`` at your convenience
        * ``service_type`` to specify type for imported objects. This type will be assigned to all objects imported through the parser
        * See the `geotrek/trekking/parsers.py <https://github.com/GeotrekCE/Geotrek-admin/blob/master/geotrek/trekking/parsers.py>`__ file for details about parsers

    .. md-tab-item:: Infrastructure

        To import infrastructure from APIDAE (ex-SITRA), define a subclass of ``geotrek.infrastructure.parsers.ApidaeInfrastructureParser`` in your ``var/conf/parsers.py`` file with the following content:

        ::

            class PicNicTable(ApidaeInfrastructureParser):
                label = "Picnic tables"
                provider = "Apidae"
                selection_id = 12345
                infrastructure_type = "Picnic table"

        Then set up appropriate values:

        * ``label`` at your convenience
        * ``infrastructure_type`` to specify type for imported objects. This type will be assigned to all objects imported through the parser
        * See the `geotrek/infrastructure/parsers.py <https://github.com/GeotrekCE/Geotrek-admin/blob/master/geotrek/infrastructure/parsers.py>`__ file for details about parsers

Activate translations
~~~~~~~~~~~~~~~~~~~~~

``expand_translations`` is an option that can be activated for a specific field in ``field_options``.
It automatically fills the translated versions of the field using multilingual data from APIDAE.

Example:

::

    field_options = {
        "name": {
            "expand_translations": True,
            "required": True
        }
    }

.. _tourinsoft-parsers:

Tourinsoft
----------

`Tourinsoft <https://www.tourinsoft.com/>`_ is a Tourism Information System developed by the company `Ingénie <https://www.ingenie.fr/systeme-d-information-touristique.html>`_ for tourism organizations in France, such as Departmental Tourism Committees (CDT), Tourism Development Agencies (ADT), and Tourist Offices. This system allows for the centralization, management, and standardized dissemination of tourism-related information.

.. md-tab-set::
    :name: importdata-tourinsoft-tabs

    .. md-tab-item:: Touristic content

        To import touristic contents from Tourinsoft, define a subclass of ``geotrek.tourism.parsers.TouristicContentTourinsoftParser`` in your ``var/conf/parsers.py`` file with the following content:

        ::

            class RestaurationParser(TouristicContentTourinsoftParser):
                """Restauration parsers"""
                label = "Restauration"
                category = "Restauration"
                url = "<Touristic content data feed URL"  # In the form https://api-v3.tourinsoft.com/api/syndications/decibelles-data.tourinsoft.com/<id>?format=json"

        Then set up appropriate values:

        * ``label`` at your convenience,
        * ``category`` to select in which Geotrek category imported objects should go.
        * See the `geotrek/tourism/parsers.py <https://github.com/GeotrekCE/Geotrek-admin/blob/master/geotrek/tourism/parsers.py>`__  file for details about parsers


.. _cirkwi-parsers:

Cirkwi
------

`Cirkwi <https://www.cirkwi.com/>`_ is a platform for distributing tourism content (treks, points of interest, digital guides) aimed at tourism professionals. It helps promote tourism data through websites, mobile apps, or interactive kiosks using widgets or APIs, relying on a library of shared or proprietary content.

.. note ::

    By default, imported content is automatically published.

.. md-tab-set::
    :name: importdata-cirkwi-tabs

    .. md-tab-item:: Treks

        .. warning::
            This parser is compatible with instances operating in :ref:`Non-Dynamic Segmentation <configuration-dynamic-segmentation>` (NDS) mode only.

        To import treks from Cirkwi, define a subclass of ``geotrek.trekking.parsers.CirkwiTrekParser`` in your ``var/conf/parsers.py`` file with the following content:

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


        * See the `geotrek/trekking/parsers.py <https://github.com/GeotrekCE/Geotrek-admin/blob/master/geotrek/trekking/parsers.py>`__  file for details about parsers

    .. md-tab-item:: Touristic contents

        To import treks from Cirkwi, define a subclass of ``geotrek.trekking.parsers.CirkwiTouristicContentParser`` in your ``var/conf/parsers.py`` file with the following content:
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


        * See the `geotrek/tourism/parsers.py <https://github.com/GeotrekCE/Geotrek-admin/blob/master/geotrek/tourism/parsers.py>`__  file for details about parsers

.. seealso::

  To import Geotrek treks and POIs into Cirkwi's format you can check :ref:`this section (french)  <geotrek-ignrando-cirkwi-api>`.


.. _lei-parsers:

LEI
---

The **LEI** (Lieu d’Échanges et d’Informations) was the former shared tourism information system used in Alsace to centralize and distribute regional tourism data (accommodations, events, sites, etc.).

.. md-tab-set::
    :name: importdata-lei-tabs

    .. md-tab-item:: Touristic contents

        To import touristic contents from LEI, define a subclass of ``geotrek.tourism.parsers.LEITouristicContentParser`` in your ``var/conf/parsers.py`` file with the following content:

        ::

            class XXXLEIEventParser(LEITouristicEventParser):
                label = "LEI TouristicEvent"
                url = "https://url.asp"

        * See the `geotrek/tourism/parsers.py <https://github.com/GeotrekCE/Geotrek-admin/blob/master/geotrek/tourism/parsers.py>`__  file for details about parsers

    .. md-tab-item:: Touristic events

        To import touristic events from LEI, define a subclass of ``geotrek.tourism.parsers.LEITouristicEventParser`` in your ``var/conf/parsers.py`` file with the following content:

        ::

            class XXXLEIEventParser(LEITouristicEventParser):
                label = "LEI TouristicEvent"
                url = "https://url.asp"

        * See the `geotrek/tourism/parsers.py <https://github.com/GeotrekCE/Geotrek-admin/blob/master/geotrek/tourism/parsers.py>`__  file for details about parsers

.. _marque-esprit-parc-parsers:

Marque Esprit Parc
------------------

The `Esprit Parc <https://www.espritparcnational.com/>`_ brand promotes tourist offers committed to the preservation of nature and local know-how in national park areas.

.. md-tab-set::
    :name: importdata-espritparc-tabs

    .. md-tab-item:: Touristic content

        To import touristic contents from Esprit Parc, define a subclass of ``geotrek.tourism.parsers.EspritParcParser`` in your ``var/conf/parsers.py`` file with the following content:

        ::

            class XXXEspritParcParser(EspritParcParser):
                label = "Marque Esprit Parc"
                url = "https://gestion.espritparcnational.com/ws/?f=getProduitsSelonParc&codeParc=XXX"

        Then set up appropriate values:

        * ``XXX`` by unique national park code (ex: PNE)
        * See the `geotrek/tourism/parsers.py <https://github.com/GeotrekCE/Geotrek-admin/blob/master/geotrek/tourism/parsers.py>`__  file for details about parsers

        .. note::
            You can duplicate the class. Each class must have a different name.
            In this case categories and types in Geotrek database have to be the same as in Esprit parc database. Otherwise missing categories and types will be created in Geotrek database.

        .. note::
            Imported contents will be automatically published and approved (certified).

        If you use an url that filters a **unique category**, you can change its name. Example to get only Honey products and set the Geotrek category and type in which import them:

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


.. _osm-parsers:

OpenStreetMap
-------------

`OpenStreetMap <https://www.openstreetmap.org/>`_ (OSM) is a collaborative, open-source mapping database that provides freely accessible geographic data, maintained by a global community of contributors. OpenStreetMap parsers retrieve OSM data using the `Overpass API <https://wiki.openstreetmap.org/wiki/Overpass_API>`_.

Basic configuration of OSM parsers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. md-tab-set::
    :name: importdata-osm-tabs

    .. md-tab-item:: Information desks

        To import information desks from OpenStreetMap, define a subclass of ``geotrek.tourism.parsers.InformationDeskOpenStreetMapParser`` in your ``var/conf/parsers.py`` file with the following content:

        ::

            class MaisonDuParcParser(InformationDeskOpenStreetMapParser):
                provider = "OpenStreetMap"
                tags = [{"amenity": "ranger_station"}]
                default_fields_values = {"name": "Maison du Parc"}
                type = "Maisons du parc"

        Then set up appropriate values:

        * ``tags`` to filter the objects imported from OpenStreetMap (for more information, see the documentation for OSM parsers query configuration below)
        * ``default_fields_values`` to define a value that will be assigned to a specific field when the external object does not contain the corresponding tag
        * ``type`` to specify the Geotrek type for imported objects
        * See the `geotrek/tourism/parsers.py <https://github.com/GeotrekCE/Geotrek-admin/blob/master/geotrek/tourism/parsers.py>`__  file for details about parsers

        You can duplicate the class to import different types of information desks. In that case, each class must have a unique name and provider label.

    .. md-tab-item:: Touristic contents

        To import touristic contents from OpenStreetMap, define a subclass of ``geotrek.tourism.parsers.OpenStreetMapTouristicContentParser`` in your ``var/conf/parsers.py`` file with the following content:

        ::

            class RestaurantParser(OpenStreetMapTouristicContentParser):
                provider = "OpenStreetMap"
                tags = [{"amenity": "restaurant"}]
                default_fields_values = {"name": "restaurant"}
                category = "Restaurants"
                type1 = "Restaurant"

        Then set up appropriate values:

        * ``tags`` to filter the objects imported from OpenStreetMap (for more information, see the documentation for OSM parsers query configuration below)
        * ``default_fields_values`` to define a value that will be assigned to a specific field when the external object does not contain the corresponding tag
        * ``category`` (mandatory), ``type1`` and ``type2`` (optional) to select in which Geotrek category/type imported objects should go. ``type1`` and ``type2`` can have multiple values (ex: ``type1 = ["Restaurant", "Hotel"]``)
        * ``portal`` to select in which portal(s) the objects should appear. Multiple portals can be assigned (ex: ``portal = ["portal 1", "portal 2"]``)
        * ``source`` to select the data source. Multiple sources can be assigned (ex: ``source = ["source 1", "source 2"]``)
        * ``themes`` to select the corresponding theme(s) of the parsed objects. Multiple themes can be assigned (ex: ``themes = ["theme 1", "theme 2"]``)
        * See the `geotrek/tourism/parsers.py <https://github.com/GeotrekCE/Geotrek-admin/blob/master/geotrek/tourism/parsers.py>`__  file for details about parsers


    .. md-tab-item:: Points of interest

        To import point of interest (POI) from OpenStreetMap, define a subclass of ``geotrek.tourism.parsers.OpenStreetMapPOIParser`` in your ``var/conf/parsers.py`` file with the following content:

        ::

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

        * ``tags`` to filter the objects imported from OpenStreetMap (for more information, see the documentation for OSM parsers query configuration below)
        * ``default_fields_values`` to define a value that will be assigned to a specific field when the external object does not contain the corresponding tag
        * ``type`` to specify the Geotrek type for imported objects
        * See the `geotrek/trekking/parsers.py <https://github.com/GeotrekCE/Geotrek-admin/blob/master/geotrek/trekking/parsers.py>`__  file for details about parsers

        You can duplicate the class to import different types of points of interest. In that case, each class must have a unique name and provider label.

    .. md-tab-item:: Districts

        To import districts from OpenStreetMap, define a subclass of ``geotrek.tourism.parsers.OpenStreetMapDistrictParser`` in your ``var/conf/parsers.py`` file with the following content:

        ::

            class DistrictParser(OpenStreetMapDistrictParser):
                provider = "OpenStreetMap"
                tags = [
                    [{"boundary": "administrative"}, {"admin_level": "6"}], # departement
                    [{"boundary": "administrative"}, {"admin_level": "4"}], # region
                ]
                default_fields_values = {"name": "district"}

        Then set up appropriate values:

        * ``tags`` to filter the objects imported from OpenStreetMap (for more information, see the documentation for OSM parsers query configuration below)
        * ``default_fields_values`` to define a value that will be assigned to a specific field when the external object does not contain the corresponding tag
        * See the `geotrek/zoning/parsers.py <https://github.com/GeotrekCE/Geotrek-admin/blob/master/geotrek/zoning/parsers.py>`__  file for details about parsers

    .. md-tab-item:: Restricted areas

        To import restricted areas from OpenStreetMap, define a subclass of ``geotrek.tourism.parsers.OpenStreetMapRestrictedAreaParser`` in your ``var/conf/parsers.py`` file with the following content:

        ::

            class RegionalNatureParkParser(OpenStreetMapDistrictParser):
                provider = "OpenStreetMap"
                tags = [{"protection_title"="parc naturel régional"}]
                default_fields_values = {"name": "parc naturel régional"}
                area_type = "Inconnu"

        Then set up appropriate values:

        * ``tags`` to filter the objects imported from OpenStreetMap (for more information, see the documentation for OSM parsers query configuration below)
        * ``default_fields_values`` to define a value that will be assigned to a specific field when the external object does not contain the corresponding tag
        * ``area_type`` to specify the restricted area type for imported objects
        * See the `geotrek/zoning/parsers.py <https://github.com/GeotrekCE/Geotrek-admin/blob/master/geotrek/zoning/parsers.py>`__  file for details about parsers

    .. md-tab-item:: Signage

        To import signage from OpenStreetMap, define a subclass of ``geotrek.tourism.parsers.OpenStreetMapSignageParser`` in your ``var/conf/parsers.py`` file with the following content:

        ::

            class DirectionalParser(OpenStreetMapSignageParser):
                provider = "OpenStreetMap"
                tags = [{"information": "guidepost"}]
                default_fields_values = {"name": "guidepost"}
                type = "Directionelle"

        Then set up appropriate values:

        * ``tags`` to filter the objects imported from OpenStreetMap (for more information, see the documentation for OSM parsers query configuration below)
        * ``default_fields_values`` to define a value that will be assigned to a specific field when the external object does not contain the corresponding tag
        * ``type`` to specify the Geotrek type for imported objects
        * See the `geotrek/signage/parsers.py <https://github.com/GeotrekCE/Geotrek-admin/blob/master/geotrek/signage/parsers.py>`__  file for details about parsers

    .. md-tab-item:: Infrastructures

        To import infrastructures from OpenStreetMap, define a subclass of ``geotrek.tourism.parsers.OpenStreetMapInfrastructureParser`` in your ``var/conf/parsers.py`` file with the following content:

        ::

            class TableParser(OpenStreetMapInfrastructureParser):
                provider = "OpenStreetMap"
                tags = [
                    {"leisure": "picnic_table"},
                    {"tourism": "picnic_table"}
                ]
                default_fields_values = {"name": "picnic table"}
                type = "Table"

        Then set up appropriate values:

        * ``tags`` to filter the objects imported from OpenStreetMap (for more information, see the documentation for OSM parsers query configuration below)
        * ``default_fields_values`` to define a value that will be assigned to a specific field when the external object does not contain the corresponding tag
        * ``type`` to specify the Geotrek type for imported objects
        * See the `geotrek/infrastructure/parsers.py <https://github.com/GeotrekCE/Geotrek-admin/blob/master/geotrek/infrastructure/parsers.py>`__  file for details about parsers

        You can duplicate the class to import different types of information desks. In that case, each class must have a unique name and provider label.

    .. md-tab-item:: Outdoor sites

        To import outdoor sites from OpenStreetMap, define a subclass of ``geotrek.tourism.parsers.OpenStreetMapOutdoorSiteParser`` in your ``var/conf/parsers.py`` file with the following content:

        ::

            class ClimbingSiteParser(OpenStreetMapOutdoorSiteParser):
                provider = "OpenStreetMap"
                tags = [{"sports": "climbing"}]
                default_fields_values = {"name": "climbing site"}
                practice = "Escalade"

        Then set up appropriate values:

        * ``tags`` to filter the objects imported from OpenStreetMap (for more information, see the documentation for OSM parsers query configuration below)
        * ``default_fields_values`` to define a value that will be assigned to a specific field when the external object does not contain the corresponding tag
        * ``practice`` to select in which Geotrek practice imported objects should go.
        * ``portal`` to select in which portal(s) the objects should appear. Multiple portals can be affected (ex: portal = ["portal 1", "portal 2"])
        * ``source`` to select the data source. Multiple sources can be affected (ex: source = ["source 1", "source 2"])
        * ``themes`` to select the corresponding theme(s) of the parsed objects. Multiple themes can be affected (ex: themes = ["theme 1", "theme 2"])
        * See the `geotrek/outdoor/parsers.py <https://github.com/GeotrekCE/Geotrek-admin/blob/master/geotrek/outdoor/parsers.py>`__  file for details about parsers

    .. md-tab-item:: Cities

        To import cities from OpenStreetMap, define a subclass of ``geotrek.zoning.parsers.OpenStreetMapCityParser`` in your ``var/conf/parsers.py`` file with the following content:

        ::

            class CityParser(OpenStreetMapCityParser):
                provider = "OpenStreetMap"
                tags = [
                    [{"boundary": "administrative"}, {"admin_level": "8"}],
                ]
                default_fields_values = {"name": "city"}
                code_tag = "ref:INSEE"

        Then set up appropriate values:

        * ``tags`` to filter the objects imported from OpenStreetMap (for more information, see the documentation for OSM parsers query configuration below)
        * ``default_fields_values`` to define a value that will be assigned to a specific field when the external object does not contain the corresponding tag
        * ``code_tag`` to specify the OpenStreetMap tag that contains the code information (e.g., in France, code_tag = "ref:INSEE"). If no value is defined, the code will not be included.
        * See the `geotrek/zoning/parsers.py <https://github.com/GeotrekCE/Geotrek-admin/blob/master/geotrek/zoning/parsers.py>`__ file for details about parsers

Query configuration
~~~~~~~~~~~~~~~~~~~

By default, the parser uses the German Overpass server:
``https://overpass-api.de/api/interpreter/``.

You can override this by setting a custom URL in the ``url`` attribute of the ``OpenStreetMapParser`` class.

Overpass queries are written in `Overpass QL <https://wiki.openstreetmap.org/wiki/Overpass_API/Overpass_QL>`_. Query configuration is handled through the ``query_settings`` attribute, which includes:

* ``bbox_margin`` (default: ``0.0``): A proportional buffer applied to the query bounding box. It expands the area by a fraction of its width to ensure surrounding features are included. (exemple: if bbox_margin is 0.05 then the bbox will be expanded by 5%)

* ``osm_element_type`` (default: ``nwr``): Specifies the types of elements to retrieve: ``"node"``, ``"way"``, ``"relation"``, or ``"nwr"`` (all three).

* ``output`` (default: ``"geom"``): Specifies the data returned by the Overpass API.
    * ``geom``: return the object type, the object ID, the tags and the geometry
    * ``tags``: return the object type, the object ID and the tags

The ``tags`` attribute defines the set of tag filters to be used with the Overpass API (see `MapFeatures <https://wiki.openstreetmap.org/wiki/Map_features>`_  to get a list of existing tags).
It is a list where each element is either:

* A **dictionary**: representing a single tag filter (e.g., ``{"highway": "bus_stop"}``)

* A **list of dictionaries**: representing a logical AND across all contained tags (e.g., [{"boundary": "administrative"}, {"admin_level": "4"}] means the object must have both tags).

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
~~~~~~~~~~~~~~~~~~~~~~~~~~

OpenStreetMap supports multilingual fields using tags like ``name:fr``, following the ISO 639-1 standard.

During import, the parser maps translated fields (e.g., ``name``, ``description``) based on the model and the languages defined in ``settings.MODELTRANSLATION_LANGUAGES``. For each language, it creates a mapping such as ``name_fr`` → ``name:fr``.

For the default language (``settings.MODELTRANSLATION_DEFAULT_LANGUAGE``), a special mapping is applied: it includes a fallback to the base tag (e.g., ``name``) and maps it to the base Geotrek field name (e.g., ``name``). This allows for filtering operations without relying directly on the default language code.

If a translation is missing, the field remains unset unless a fallback value is provided in ``default_fields_values`` using the pattern ``{field}_{lang}``.

When no translation exists for the default language, the base OpenStreetMap tag (e.g., ``name``) is used. This can lead to incorrect language display if the OSM default does not match the Geotrek instance’s default language.

Translation logic can be customized in custom parsers by overriding the ``translation_fields`` method.

Attachments
~~~~~~~~~~~
``OpenStreetMapParser`` automatically attaches files from ``wikimedia_commons`` and ``image`` tags found in the data.
A ``CC BY-SA 4.0`` license is assigned to each imported file, as specified by the OpenStreetMap license.

For more information on how attachments work, consult :ref:`this section <import-attachments>`.


.. _importing-from-multiple-sources:

Import from multiple sources
============================

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

.. _further_information:

Further information
===================

Overriding base parsers methods
-------------------------------

Base parser classes and built-in configurable parsers implement parsing logic that is either generic or specific to certain data sources.
You can override these methods in your custom parsers to adapt behavior to your needs.

However, this should only be done when necessary, as custom implementations will prevent your parsers from benefitting from future improvements or bug fixes in the base methods.

.. _import-attachments:

Detailed operation of attachment parsing
----------------------------------------

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
~~~~~~~~~~

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
~~~~~~~~~~~~~~~~~~~~~

The ``filter_attachments`` method formats the external source data to match with the internal format.

If the attachment data has a different structure than the default ``filter_attachments``, the method must be overridden.

See the `geotrek/common/parsers.py <https://github.com/GeotrekCE/Geotrek-admin/blob/master/geotrek/common/parsers.py>`__ file to see more about attachments.

.. _geometry-filtering:

Geometry filtering in Geotrek parsers
-------------------------------------

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

Conditional deletion with ``delete = True``
-------------------------------------------

If ``delete`` attribut is set to ``True``, the parser will automatically **delete existing objects** of the current model
that **do not intersect** the reference geometry.

.. note::

   Deletion only affects objects of the model handled by the current parser. Other models are not impacted.

Linking source objects via `eid`
--------------------------------

Starting with **Geotrek-admin 2.117.0**, the `eid` (external ID) field displayed on the object detail page can now include a clickable link to the original source object.

To enable this, a new database model called **Provider** has been added. This model can be managed through the Django admin interface and includes the following fields:

- **Name**
- **Link template** (an HTML snippet used to build the link using the `eid`)
- **Copyright**

The link template should contain the `{{object.eid}}` placeholder, which will be replaced by the actual external ID. For example:

.. code-block:: html

   <a href="https://example.com/objects/{{object.eid}}" target="_blank">{{object.eid}}</a>

Fixtures are available for two providers: **OpenStreetMap** and **Apidae**. These predefined Provider records can be loaded during a new installation.
See the :ref:`fixture documentation <loading-fixtures>` to see more about fixtures.

.. note::

    These fixtures are intended for new installations only. When upgrading an existing system, Provider records will be created automatically based on the existing `provider` field in the database. After upgrading, you must manually fill in the link template and copyright.

    You can reuse the link templates provided in the fixture files, available here:
    `Provider fixtures on GitHub <https://github.com/GeotrekCE/Geotrek-admin/tree/master/geotrek/common/fixtures/basic.json#L242>`_

Apply parsers changes
----------------------

To apply changes when using Debian, you may have to run ``sudo service geotrek restart``.
