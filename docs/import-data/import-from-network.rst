====================
Import from network
====================

.. _import-data-from-a-remote-geotrek-instance:

Import data from an other Geotrek-admin (aggregator)
=====================================================

Importing from a Geotrek-admin instance works the same way as from SIT.
A usecase for this is to aggregate data from several Geotrek-admin instances.

.. important::
    Importing data from a remote Geotrek-admin instance does not work with dynamic segmentation, your instance where you import data
    must have :ref:`dynamic segmentation disabled <configuration-dynamic-segmentation>`.

Import data from another instance
----------------------------------

Here is an example to import treks from another instance :

1. Edit ``/opt/geotrek-admin/var/conf/parsers.py`` file with the following content:

.. code-block:: python

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

2. Then run in command line:

.. md-tab-set::
    :name: import-from-parser-tabs

    .. md-tab-item:: With Debian

         .. code-block:: python

          sudo geotrek import DemoGeotrekTrekParser

    .. md-tab-item:: With Docker

         .. code-block:: python
    
          docker compose run --rm web ./manage.py import  DemoGeotrekTrekParser

Treks are now imported into your own instance.

.. seealso::

  To set up automatic commands you can check the :ref:`Automatic commands section <automatic-commands>`.

Import from several Geotrek-admin instances
--------------------------------------------

Here is an example to import data from several instances :

1. Create the aggregator configuration file

.. example:: Example of aggregator configuration file
    :collapsible:

    ::

      {
        "Instance1": {
         "url": "https://remote-geotrek-admin1.net",  # replace url with remote
          "portals": ["6"],
          "data_to_import":  [
            "Trek",
            "TouristicContent",
            "TouristicEvent",
            "Signage",
            "Infrastructure",
            "Site",
            "Course",
            "InformationDesk"
          ],
          "create": true,
          "mapping": {
            "trek_practice": {
              "Pédestre": ["A pied"],
              "VTT": ["VTT"],
              "Équestre": ["Cheval"],
              "Trail": ["Trail"]
            },
            "trek_difficulty": {
              "Très facile": ["Très facile"],
              "Facile": ["Facile"],
              "Moyen": ["Moyen"],
              "Difficile": ["Difficile"]
            },
            "trek_accessibility": {
               "Famille": ["Famille"],
               "Poussette": ["Poussette"],
               "Joelette": ["Joelette"]
             },
            "trek_route": {
              "Aller-retour": ["Aller-retour"],
              "Itinérance": ["Séjour itinérant"],
              "Traversée": ["Traversée"],
              "Étape":["Etape"],
              "Boucle": ["Boucle"],
              "Descente": ["Descente"]
            },
            "trek_network": {
              "En ville": ["En ville"],
              "Vélo": ["VTT"],
              "Trail": ["Trail"],
              "Sentier thématique": ["Sentier thématique"],
              "Snow trail": ["Snow trail"],
              "PR": ["PR"],
              "GR": ["GR"],
              "GRP": ["GRP"],
              "Équestre": ["Piste équestre"],
              "Itinérance VTT": ["Itinérance VTT"]
            },
            "theme":  {
              "Archéologie": ["Archéologie"],
              "Patrimoine et histoire": ["Histoire et architecture"],
              "Col et sommet": ["Sommet", "Col"],
              "Faune": ["Faune"],
              "Flore et forêt": ["Flore"],
              "Géologie": ["Géologie"],
              "Eau": ["Lac et glacier"],
              "Pastoralisme": ["Pastoralisme"],
              "Point de vue": ["Point de vue"],
              "Refuge": ["Refuge"]
            },
            "outdoor_practice": {
              "Canoë-kayak": ["Canoë-kayak"],
              "Escalade": ["Escalade"],
              "Via ferrata": ["Via ferrata"]
            }
          }
        },
        "Instance2": {
          "url": "https://remote-geotrek-admin2.net",  # replace url with remote
          "all_datas": true,
          "create": true,
          "data_to_import": [
            "Trek",
            "TouristicContent",
            "TouristicEvent",
            "Signage",
            "Infrastructure",
            "Site",
            "Course",
            "InformationDesk"
          ], 
          "mapping": {
            "trek_practice": {
              "Pédestre": ["Pédestre"],
              "VTT": ["VTT"],
              "Équestre": ["Cheval"],
              "Séjours": ["Itinérance"]
            },
            "trek_difficulty": {
              "Très facile": ["Facile"],
              "Facile": ["Moyen"],
              "Moyen": ["Difficile"],
              "Difficile": ["Actif"]
            },
            "trek_accessibility": {
               "Poussette": ["Poussette"],
               "Joelette": ["Joelette"]
             },
            "trek_route": {
              "Aller-retour": ["Aller-retour"],
              "Itinérance": ["Itinérance"],
              "Traversée": ["Traversée"],
              "Étape":["Etape"],
              "Boucle": ["Boucle"]
            },
            "trek_network": {
              "Vélo": ["VTT"],
              "PR": ["PR"],
              "GR": ["GR"],
              "GRP": ["GRP"],
              "Équestre": ["Piste équestre"]
            },
            "theme":  {
              "Archéologie": ["Archéologie et histoire"],
              "Patrimoine et histoire": ["Architecture"],
              "Col et sommet": ["Col et sommet"],
              "Faune": ["Faune"],
              "Flore et forêt": ["Flore"],
              "Géologie": ["Géologie"],
              "Eau": ["Lac et glacier"],
              "Pastoralisme": ["Pastoralisme"],
              "Point de vue": ["Point de vue"],
              "Refuge": ["Refuge / Abri"]
            },
            "outdoor_practice": {
              "Canoë-kayak": ["Canoë-kayak"],
              "Vol libre": ["Vol libre"],
              "Escalade": ["Escalade"],
              "Via ferrata": ["Via ferrata"]
             }
          }
        }
      }

2. Edit ``/opt/geotrek-admin/var/conf/parsers.py`` file with the following content:

.. code-block:: python

  class GeotrekAggregator(GeotrekAggregatorParser):
      filename = "var/conf/aggregator_configuration.json"

      def __init__(self, progress_cb=None, user=None, encoding='utf8'):
          self.mapping_model_parser["Signage"] = ("var.conf.parsers", "GeotrekUnpublishedSignageParser")
          self.mapping_model_parser["InformationDesk"] = ("var.conf.parsers", "GeotrekInformationDeskParser")
          super().__init__(progress_cb, user, encoding)

3. Then run in command line:

.. md-tab-set::
    :name: import-aggregate-data-tabs

    .. md-tab-item:: With Debian

         .. code-block:: python

          sudo geotrek import GeotrekAggregatorParser

    .. md-tab-item:: With Docker

         .. code-block:: python
    
          docker compose run --rm web ./manage.py import  GeotrekAggregatorParser

Aggregate data are now imported into the Geotrek-admin aggregator.

.. seealso::

  To set up automatic commands you can check the :ref:`Automatic commands section <automatic-commands>`.

.. _sensitive-areas-import:

Sensitive Areas Import
=======================

Geotrek-admin provides tools to import sensitive areas data when the module is enabled. The imports can be done through the web interface or the command line. Below are the available options:

Import from Biodiv'Sports
----------------------------

Automatically import sensitive areas from Biodiv'Sports:

From the web interface
~~~~~~~~~~~~~~~~~~~~~~~

1. Click on the **user button** (top-right corner) and go to **Imports**.
2. Under **Data to import from network**, select **Biodiv'Sports** and click **Import**.
3. Wait for the import process to complete.
4. Check the Sensitivity module in Geotrek to view the imported data.

.. warning::
    If no data appears, Biodiv'Sports might not have data for your region. Consider adding your data directly to Biodiv'Sports for shared access across users.

From the command line
~~~~~~~~~~~~~~~~~~~~~~~

.. md-tab-set::
    :name: import-from-biodiv-tabs

    .. md-tab-item:: Example with Debian

         .. code-block:: python

          sudo geotrek import geotrek.sensitivity.parsers.BiodivParser

    .. md-tab-item:: Example with Docker

         .. code-block:: python
    
          docker compose run --rm web ./manage.py import  geotrek.sensitivity.parsers.BiodivParser

Import from a Shapefile
--------------------------

Sensitive areas can also be imported from an ESRI Shapefile (zipped). Ensure the following:

- The archive must include ``.shp``, ``.shx``, ``.dbf``, ``.prj``, etc.
- Field names must be configured correctly, as detailed below.

.. warning::
    Re-importing the same file will create duplicates.

**Species sensitive areas**:

- ``espece``: Species name (required, must exist in Biodiv'Sports).
- ``contact``: Optional contact information (text or HTML).
- ``descriptio``: Optional description (text or HTML).

**Regulatory sensitive areas**:

- ``name``: Area name (required).
- ``contact``: Optional contact information (text or HTML).
- ``descriptio``: Optional description (text or HTML).
- ``periode``: Months during which the area is sensitive (comma-separated, e.g., ``6,7,8`` for June-August).
- ``practices``: Practices associated with the area (comma-separated).
- ``url``: Optional URL for the record.

.. warning::
    Field names in shapefiles are limited to 10 characters (e.g., ``descriptio``).

From the web interface
~~~~~~~~~~~~~~~~~~~~~~~

1. Click on the **user button** (top-right corner) and go to **Imports**.
2. Select the data type (**species** or **regulatory area**).
3. Upload the zipped shapefile and select the appropriate encoding (UTF-8 or Windows-1252).
4. Click **Import** and monitor the progress.
5. View the import report for details.

.. figure:: ../images/advanced-configuration/import_shapefile.png
     :alt: Import shapefile in user interface
     :align: center

     Import shapefile in user interface

From the command line
~~~~~~~~~~~~~~~~~~~~~~~

- For species sensitive areas:

.. md-tab-set::
    :name: import-species-sensitive-areas-tabs

    .. md-tab-item:: Example with Debian

         .. code-block:: python

          sudo geotrek import geotrek.sensitivity.parsers.SpeciesSensitiveAreaShapeParser <file.zip>

    .. md-tab-item:: Example with Docker

         .. code-block:: python
    
          docker compose run --rm web ./manage.py import  geotrek.sensitivity.parsers.SpeciesSensitiveAreaShapeParser <file.zip>

- For regulatory sensitive areas:

.. md-tab-set::
    :name: import-regulatory-sensitive-areas-tabs

    .. md-tab-item:: Example with Debian

         .. code-block:: python

          sudo geotrek import geotrek.sensitivity.parsers.RegulatorySensitiveAreaShapeParser <file.zip>

    .. md-tab-item:: Example with Docker

         .. code-block:: python
    
          docker compose run --rm web ./manage.py import geotrek.sensitivity.parsers.RegulatorySensitiveAreaShapeParser <file.zip>

