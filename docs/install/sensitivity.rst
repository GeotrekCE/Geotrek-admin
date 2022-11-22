.. _sensitivity-section:

===========
Sensitivity
===========


Enabling
--------

Sensitivity module is disabled by default.
To enable it, add the following code in the custom settings file:

.. code-block :: python

    # Enable sensitivity module
    INSTALLED_APPS += ('geotrek.sensitivity', )


Settings
--------

The following settings are related to sensitive areas:

.. code-block :: python

    # Default radius of sensitivity bubbles when not specified for species
    SENSITIVITY_DEFAULT_RADIUS = 100  # meters

    # Buffer around treks to intersects sensitive areas
    SENSITIVE_AREA_INTERSECTION_MARGIN = 500  # meters
    # Take care if you change this value after adding data. You should update buffered geometry in sql.
    ``` UPDATE sensitivity_sensitivearea SET geom_buffered = ST_BUFFER(geom, <your new value>); ```


Import from https://biodiv-sports.fr
------------------------------------

In user interface, in the top-right menu, clic on "Imports" and choose "Biodiv'Sports".

On command line, run

.. code-block :: bash

    sudo geotrek import geotrek.sensitivity.parsers.BiodivParser


Import from shapefile
---------------------

In user interface, in the top-right menu, go to Imports and choose "Shapefile zone sensible espèce"
or "Shapefile zone sensible réglementaire".

On command line, run:

.. code-block :: bash

    sudo geotrek import geotrek.sensitivity.parsers.SpeciesSensitiveAreaShapeParser <file.shp>

or:

.. code-block :: bash

    sudo geotrek  import geotrek.sensitivity.parsers.RegulatorySensitiveAreaShapeParser <file.shp>.

Attributes for "zones sensibles espèce" are:
 
* espece : species name. Mandatory. A species with this name must have been previously created.
* contact : contact (text or HTML format). Optional.
* descriptio : description (text or HTML format). Optional.

Attributes for "zones sensibles réglementaires" are:

* name: zone name.
* contact : contact (text or HTML format). Optional.
* descriptio : description (text or HTML format). Optional.
* periode : month numbers of zone occupation, separated by comas, without spaces (ex. « 6,7,8 » for june, july and august)
* pratiques : sport practices names, separated by comas, without spaces (ex. « Terrestre,Aérien »). A sport practice with this name must have been previously created.
* url : card url. Optional.


Sync to Geotrek-rando
---------------------

Just run:

.. code-block :: bash

    sudo geotrek sync_rando <parameters>
    
as usual. If sensitivity module is enabled, sensitive areas will be automatically synced.
