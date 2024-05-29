.. _sensitivity-usage-section:

======================
Sensitivity module usage
======================

.. note::
    The sensitivity module was developed as part of the Biodiv'Sports project to provide a central platform for sensitive areas. 

    The official address of the Geotrek instance of the BiodivSports project is: https://biodiv-sports.fr, and is the base url for the following API URLs.

###########################
Import data (automatically)
###########################

It is possible to import automatically data from Biodiv'sport. To do so, you just need to follow those steps : 

- Click on the **user link** at top right, then on **Imports**,
- Under the section **Data to import from network**, select **Biodiv'Sports **
- Click on **Import**,
- Wait a few seconds,
- The import progress is displayed on the right

When the import is done, you can check the Sensitivity module in Geotrek and you'll find data inside.

.. warning:: 
  If you don't see any data in your area, it means that Biodiv'Sport does not contains data for your territory. Then it is widely recommended to add your data directly into Biodiv'Sport, as it will be available for multiple users, and then retrieve them into your Geotrek instance. To import data in Biodiv'Sport go visit their website : https://biodiv-sports.fr


.. _Import:

############
Import areas
############

Data preparation
================

File type
---------

Imported data must be in standard ESRI shapefile format. 
The various Shapefile files (``.shp``, ``.shx``, ``.dbf``, ``.prj``, *etc*.) must be assembled in a zip archive.

.. warning::
  Please note! The description field name ``descriptio`` does not include the final ``n``, as field names are limited to 10 characters in shapefiles.

Attribute data for sensitive areas species
------------------------------------------

- ``espece``: Species name. Mandatory. A species with this name must first have been created in Biodiv'sports. Otherwise, import of the line will fail.
- ``contact``: Contact in text or HTML format. *Optional*.
- ``descriptio``: Description in text or HTML format. *Optional*. 

.. warning::
  Species name must strictly respect the species name string (accentuation, case and punctuation).

Attribute data for regulatory sensitive areas
---------------------------------------------

- ``name`` : Area name
- ``contact`` : Contact in text or HTML format. *Optional*.
- ``descriptio`` : Description in text or HTML format. *Optional*.
- ``periode``: Numbers of the months in which the area is occupied, **comma separated** and **without spaces** (e.g. ``6,7,8`` for June, July and August).
- ``practices``: Names of practices, separated by commas, without spaces (e.g. ``Terrestre,Aerien,Vertical``), see :ref:`Practices`. Otherwise, the line import will fail.
- ``url`` : Record url. *Optional*.

Import
======

- Click on the **user link** at top right, then on **Imports**,
- Select the type of data to be imported (**species** or **regulatory area**),
- Select the *.zip* file to be imported,
- Select the correct encoding (``UTF8`` or ``Windows-1252``)
- Click on **Import**,
- Wait a few seconds,
- The import progress is displayed on the right,
- Click on **Display report** to see any unimported lines.


.. warning:: 
  Relaunching an import **with the same file** will create duplicates.


#########
API usage
#########

.. note::

  You can play with API using Biodiv'Sports widget tool: https://biodivsports-widget.lpo-aura.org/


Requesting URLs
===============

.. _Common Parameters:

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


Sensitive areas
---------------

List of sensitive areas

``/api/v2/sensitivearea/``

The default output format is ``json``. To obtain output in ``geojson`` format, simply add the ``format=geojson`` parameter.

``/api/v2/sensitivearea/?format=geojson`` 

e.g. https://biodiv-sports.fr/api/v2/sensitivearea/?format=geojson

**Filtering data**

Data can be filtered through those parameters:

- ``language`` : API language (see :ref:`Common Parameters`)

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

  - Expected values: List of bbox coordinates (respectively longitude and latitude South-West then North-East corner), comma separated.
  - e.g. ``/api/v2/sensitivearea/?in_bbox=5.0,45.0,6.0,46.0``

full example https://biodiv-sports.fr/api/v2/sensitivearea/?format=geojson&language=fr&practices=1,2&period=4,5,6,7&in_bbox=5.0,45.0,6.0,46.0

**Filtering fields**

- ``fields`` : list of expected fields (see :ref:`Field Descriptions <FielDesc>`)

  - Expected values: List of field names, comma separated
  - e.g. ``/api/v2/sensitivearea/?fields=name,geometry``

- ``omit`` : list of excluded fields (see :ref:`Field Descriptions <FielDesc>`)

  - Expected values: List of field names, comma separated
  - e.g. ``/api/v2/sensitivearea/?fields=name,geometry``

.. warning::
  **GeoJSON** format expect at least `id` and `geometry` fields.


.. _FielDesc:

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
    Species informations are commons for each species areas share Zones sharing the same ``species_id`` value also share the same values for the ``name``, ``period``, ``practices`` and ``info_url`` fields.



