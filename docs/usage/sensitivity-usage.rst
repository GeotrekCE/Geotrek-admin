======================
Sensitivy module usage
======================

.. note::
    The sensitivity module was developed as part of the Biodiv'Sports project to provide a central platform for sensitive areas. 

    The official address of the GeoTrek instance of the BiodivSports project is: https://biodiv-sports.fr, and is the base url for the following API URLs.


############
Import areas
############

############
Manage areas
############


#########
API usage
#########


Base URL
========

``/api/v2/sensitivearea/`` (e.g. https://biodiv-sports.fr/api/v2/sensitivearea/)

Requesting URLs
===============

Commons parameters
------------------


If ``language`` parameter is provided, api returns directly translated field, else, a dictionnary of traductions is returned
    
e.g. ``/api/v2/sensitivearea_practice/1/?``


.. code-block:: JSON

    {
      "id":1,
      "name":{
        "fr":"Terrestre",
        "en":"Land",
        "it":null
      }
    }


e.g. ``/api/v2/sensitivearea_practice/1/?language=en``


.. code-block:: JSON

    {
      "id":1,
      "name":"Land"
    }

.. _Practices:

Sport practices
---------------


List of outdoor practices

``/api/v2/sensitivearea_practice/``

e.g. https://biodiv-sports.fr/api/v2/sensitivearea_practice/

.. .. _Structures:

.. Structures
.. ----------


.. List of outdoor practices

.. ``/api/v2/structure/``

.. e.g. https://biodiv-sports.fr/api/v2/structure/


Sensitive areas
---------------

List of sensitive areas

``/api/v2/sensitivearea/``

The default output format is ``json``. To obtain output in ``geojson`` format, simply add the ``format=geojson`` parameter.

``/api/v2/sensitivearea/?format=geojson`` (e.g. https://biodiv-sports.fr/api/v2/sensitivearea/?format=geojson)

**Filtering Data**

Data can be filtered through those parameters:

- ``language`` : API language (default is ``fr``)

  - Expected values: ``fr``, ``en``, ``es`` or ``it``
  - e.g. ``/api/v2/sensitivearea/?language=fr``

- ``period`` : Sensitivy period (monthes list)

  - Expected values: List of month number (from 1 to 12), comma separated
  - e.g. ``/api/v2/sensitivearea/?period=4,5,6,7``

- ``practices`` : Outdoor sport practices

  - Expected values: List of practices ids (see :ref:`Practices`)
  - e.g. ``/api/v2/sensitivearea/?practices=1,2``

.. - ``structure`` : Organization that declared the sensitive area. 

..   - Expected values: List of practices ids (see :ref:`Structures`)
..   - e.g. ``/api/v2/sensitivearea/?structure=1,2``

- ``in_bbox``

  - Expected values: List of bbox coordinates (respectively longitude and latitude South-West then North-East corner)
  - e.g. ``/api/v2/sensitivearea/?in_bbox=5.0,45.0,6.0,46.0``

full example https://biodiv-sports.fr/api/v2/sensitivearea/?format=geojson&language=fr&practices=1,2&period=4,5,6,7&in_bbox=5.0,45.0,6.0,46.0


**Field descriptions**


- ``id`` : local unique identifier of the sensitive area (integer).
- ``name`` : Area name (string).
- ``description`` : Area description (string in HTML format).
- ``period`` : Area occupancy for each of the 12 months of the year (ordered array of 12 Booleans).
- ``contact`` : Contact for further information about the sensitive area (string in HTML format).
- ``practices``: sports practices concerned by the hotspot (array of identifiers).
- ``info_url`` : URL containing further information about the area (URL).
- ``structure`` : Structure or acronyme that provided information on the area (string).
- ``elevation`` : Elevation used to define area sensitivity volume (globally elevation, buffer radius for areas declared as Point).
- ``geometry`` : Area GeoJSON geometry. Type is always "Polygon".
- ``species_id``: species identifier or null for regulatory areas.
- ``kml_url`` : URL of the downloadable KML file representing this regulatory zone.
- ``openair_url`` : URL of the downloadable OpenAir file representing the regulatory zone (available only for aerial activities).
- ``attachment`` : List of area attachment files.
- ``rules`` : List of regulatory rules.
- ``update_datetime``: last update timestamp.
- ``create_datetime``: create timestamp.

.. note::
    Species informations are commons for each species areas share Zones sharing the same species_id value also share the same values for the name, period, practices and info_url fields.



