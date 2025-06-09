=============
Aggregator
=============

.. abstract:: Keywords

   ``aggregator``, ``agrégateur``, ``parser``, ``cron``


.. _import-data-from-a-remote-geotrek-instance:

Import data from an other Geotrek-admin (aggregator)
=====================================================

Importing from a Geotrek-admin instance works the same way as from SIT.
A usecase for this is to aggregate data from several Geotrek-admin instances.

.. important::
  
  Importing data from a remote Geotrek-admin instance does not work with dynamic segmentation, your instance where you import data must have :ref:`dynamic segmentation disabled <configuration-dynamic-segmentation>`.

.. seealso::
 
  If you want to implement your own aggregator, refer to :ref:`the parsers developer documentation <development-parser-import>` for details and examples.

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

Use case
~~~~~~~~~

A **National Park** oversees a vast protected area that includes several administrative and natural territories. One of these territories, a **Regional Nature Park**, manages its own Geotrek-admin instance and maintains a local database of treks, points of interest, and cultural sites.

To avoid duplicating effort and to ensure data consistency across platforms, the National Park sets up a parser that connects directly to the Regional Park's Geotrek-admin. Using the ``BaseGeotrekTrekParser``, they schedule regular imports of trekking data from the remote instance.

This approach allows the National Park to:

* re-use high-quality, up-to-date data managed by local teams,
* maintain synchronization without manual intervention,
* focus on promotion rather than data entry.

This setup is ideal when working in partnership with a **single external Geotrek-admin instance**.

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

Use case
~~~~~~~~~

A **Department** wants to build a unified portal that brings together outdoor activity data from several **Geotrek-admin instances** used by local authorities, parks, and tourism offices.

Each contributing structure maintains its own data (treks, POIs, signage, events, etc.) within its own Geotrek-admin. To provide a centralized and consistent offer, the Department uses the **aggregator parser** to import and harmonize data from all these sources.

By configuring mapping rules for labels (difficulties, themes, networks, etc.), the Department ensures:

* data consistency across the unified platform,
* delegated responsibility for content maintenance to local teams,
* improved visibility of outdoor activities at the regional scale.

This model is well-suited for **multi-territorial projects**, such as regional trek portals and inter-park cooperation.


