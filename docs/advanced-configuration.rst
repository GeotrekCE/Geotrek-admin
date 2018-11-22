.. _advanced-configuration-section:

======================
ADVANCED CONFIGURATION
======================

Custom setting file
-------------------

Geotrek configuration is currently restricted to values present in ``.env`` and ``var/conf/custom.py``.

However, it is still possible to all django or geotrek settings in custom.py :

.. code-block :: python

    # coding: utf8

    from .prod import *

    # My custom value
    HIDDEN_OPTION = 3.14

All overridable setting can be found in geotrek/settings.base.py

* As for any change in ``custom.py``, re-run ``sudo systemctl restart geotrek``.


Disable modules and components
------------------------------

In order to disable a full set of features, in the custom settings file,
add the following code:

.. code-block :: python

    # Disable infrastructure and maintenance
    _INSTALLED_APPS = list(INSTALLED_APPS)
    _INSTALLED_APPS.remove('geotrek.infrastructure')
    _INSTALLED_APPS.remove('geotrek.maintenance')
    INSTALLED_APPS = _INSTALLED_APPS

In order to remove notion of trails:

.. code-block :: python

    TRAIL_MODEL_ENABLED = False

In order to remove zoning combo-boxes on list map:

.. code-block :: python

    LAND_BBOX_CITIES_ENABLED = True
    LAND_BBOX_DISTRICTS_ENABLED = True
    LAND_BBOX_AREAS_ENABLED = False

:notes:

    By doing so, some software upgrades may not be as smooth as usual.
    Never forget to mention this customization if you ask for community support.


Sensitive areas
----------------------


In order to enable sensitivity module, in the custom settings file,
add the following code:

.. code-block :: python

    # Enable sensitivity module
    INSTALLED_APPS += ('geotrek.sensitivity', )

The following settings are related to sensitive areas:

.. code-block :: python

    # Default radius of sensitivity bubbles when not specified for species
    SENSITIVITY_DEFAULT_RADIUS = 100  # meters

    # Buffer around treks to intersects sensitive areas
    SENSITIVE_AREA_INTERSECTION_MARGIN = 500  # meters



WYSIWYG editor configuration
----------------------------

Text form fields are enhanced using `TinyMCE <http://tinymce.com>`_.

Its configuration can be customized using advanced settings (see above paragraph).

For example, in order to control which buttons are to be shown, and which tags
are to be kept when cleaning-up, add this bloc :

.. code-block :: python

    TINYMCE_DEFAULT_CONFIG = {
        'theme_advanced_buttons1': 'bold,italic,forecolor,separator,code',
        'valid_elements': "img,p,a,em/i,strong/b",
    }

This will apply to all text fields.

For more information on configuration entries available, please refer to the
official documentation of *TinyMCE version 3*.


View attachments in the browser
-------------------------------

Attached files are downloaded by default by browser, with the following line,
files will be opened in the browser :

.. code-block :: python

    MAPENTITY_CONFIG['SERVE_MEDIA_AS_ATTACHMENT'] = False


Change or add WMTS tiles layers (IGN, OSM, Mapbox...)
-----------------------------------------------------

By default, you have 2 basemaps layers in your Geotrek-admin (OSM and OSM black and white). 

You can change or add more basemaps layers.

Specify the tiles URLs this way in your custom Django setting file:

.. code-block :: python

    LEAFLET_CONFIG['TILES'] = [
        ('OSM', 'http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', u'© OpenStreetMap Contributors'),
        ('OpenTopoMap', 'http://a.tile.opentopomap.org/{z}/{x}/{y}.png', u'Map data: © OpenStreetMap contributors, SRTM | Map style: © OpenTopoMap (CC-BY-SA)'),
    ]

Example with IGN and OSM basemaps : 

.. code-block :: python

    LEAFLET_CONFIG['TILES'] = [
        ('IGN Scan', 'http://gpp3-wxs.ign.fr/YOURAPIKEY/geoportail/wmts?LAYER=GEOGRAPHICALGRIDSYSTEMS.MAPS&EXCEPTIONS=text/xml&FORMAT=image/jpeg&SERVICE=WMTS&VERSION=1.0.0&REQUEST=GetTile&STYLE=normal&TILEMATRIXSET=PM&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}', u'© IGN Geoportail'),
        ('IGN Scan Express', 'http://gpp3-wxs.ign.fr/YOURAPIKEY/geoportail/wmts?LAYER=GEOGRAPHICALGRIDSYSTEMS.MAPS.SCAN-EXPRESS.STANDARD&EXCEPTIONS=text/xml&FORMAT=image/jpeg&SERVICE=WMTS&VERSION=1.0.0&REQUEST=GetTile&STYLE=normal&TILEMATRIXSET=PM&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}', u'© IGN Geoportail'),
        ('IGN Ortho', 'http://gpp3-wxs.ign.fr/YOURAPIKEY/geoportail/wmts?LAYER=ORTHOIMAGERY.ORTHOPHOTOS&EXCEPTIONS=text/xml&FORMAT=image/jpeg&SERVICE=WMTS&VERSION=1.0.0&REQUEST=GetTile&STYLE=normal&TILEMATRIXSET=PM&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}', u'© IGN Geoportail'),
        ('IGN Cadastre', 'http://gpp3-wxs.ign.fr/YOURAPIKEY/geoportail/wmts?LAYER=CADASTRALPARCELS.PARCELS&EXCEPTIONS=text/xml&FORMAT=image/png&SERVICE=WMTS&VERSION=1.0.0&REQUEST=GetTile&STYLE=bdparcellaire_o&TILEMATRIXSET=PM&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}', u'© IGN Geoportail'),
        ('OSM', 'http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', u'© OpenStreetMap contributors'),
        ('OSM Mapbox Outdoors', 'https://api.mapbox.com/v4/mapbox.outdoors/{z}/{x}/{y}.png?access_token=pk.YOURAPIKEY', u'© OpenStreetMap contributors / Mapbox'),
        ('OSM Stamen Terrain', 'http://tile.stamen.com/terrain/{z}/{x}/{y}.jpg', u'© OpenStreetMap contributors / Stamen Design'),
        ('OpenTopoMap', 'http://a.tile.opentopomap.org/{z}/{x}/{y}.png', u'Map data: © OpenStreetMap contributors, SRTM | Map style: © OpenTopoMap (CC-BY-SA)'),
    ]

To use IGN Geoportail WMTS tiles API, you need an API key with subscribing on http://professionnels.ign.fr/visualisation. Choose WebMercator WMTS tiles.

External authent
----------------

You can authenticate user against a remote database table or view.

To enable this feature, fill *authent_dbname* and other fields in ``etc/settings.ini``.

Expected columns in table/view are :

* username : string (*unique*)
* first_name : string
* last_name : string
* password : string (simple md5 encoded, or full hashed and salted password)
* email : string
* level : integer (1: readonly, 2: redactor, 3: path manager, 4: trekking manager, 6: administrator)
* structure : string
* lang : string (language code)


:notes:

    User management will be disabled from Administration backoffice.

    In order to disable remote login, just remove *authent_dbname* value in settings
    file, and update instance (see paragraph above).

    Geotrek can support many types of users authentication (LDAP, oauth, ...), contact-us
    for more details.


Map layers colors and style
---------------------------

All layers colors can be customized from the settings.
See `Leaflet reference <http://leafletjs.com/reference.html#path>`_ for vectorial
layer style.

* To apply these style changes, re-run ``sudo systemctl restart geotrek``.

.. code-block :: python

    MAP_STYLES['path'] = {'color': 'red', 'weight': 5}

Or change just one parameter (the opacity for example) :

.. code-block :: python

    MAP_STYLES['city']['opacity'] = 0.8


Regarding colors that depend from database content, such as land layers
(physical types, work management...) or restricted areas. We use a specific
setting that receives a list of colors :

.. code-block :: python

    COLORS_POOL['restrictedarea'] = ['#ff00ff', 'red', '#ddddd'...]


See the default values in ``geotrek/settings/base.py`` for the complete list
of available styles.

**Restart** the application for changes to take effect.


External raster layers
----------------------

It is possible to add overlay tiles layer on maps. For example, it can be useful to:

* Get the cadastral parcels on top of satellite images
* Home made layers (*with Tilemill or QGisMapserver for example*).
  Like the park center borders, traffic maps, IGN BDTopo® or even the Geotrek paths
  that are marked as invisible in the database!

In ``custom.py``, just add the following lines:

.. code-block :: python

    LEAFLET_CONFIG['OVERLAYS'] = [
        ('Coeur de parc', 'http://serveur/coeur-parc/{z}/{x}/{y}.png', '&copy; PNF'),
    ]


Expected properties
~~~~~~~~~~~~~~~~~~~

For ``GeoJSON`` files, you can provide the following properties :

* ``title``: string
* ``description``: string
* ``website``: string
* ``phone``: string
* ``pictures``: list of objects with ``url`` and ``copyright`` attributes
* ``category``: object with ``id`` and ``label`` attributes


Disable darker map backgrounds
------------------------------

Since IGN map backgrounds are very dense and colourful, a dark opacity is
applied. In order to disable, change this MapEntity setting :

.. code-block:: python

    MAPENTITY_CONFIG['MAP_BACKGROUND_FOGGED'] = False


Override public document OpenOffice template
--------------------------------------------

WARNING: Documentation to be updated. Geotrek-admin now uses Weasyprint to create public PDF based on HTML templates
and no more on ODT templates. Default HTML templates are in ``geotrek/trekking/templates/`` and can be copied in ``var/conf/extra_templates/`` with same path and file names to be overriden.

Copy the file ``geotrek/trekking/templates/trekking/trek_public.odt`` to
``var/conf/extra_templates/trekking/trek_public.odt``.

Edit the copy using *OpenOffice*.

.. note ::

    The default template may change in the future versions. You will be
    in charge of porting the modification to your copy.


Custom font in public document OpenOffice template
--------------------------------------------------

In order to use custom fonts in trek PDF, it is necessary to install the
font files on the server.

*Microsoft* fonts like *Arial* and *Verdana* can be installed via the package
manager ::

    sudo apt-get install ttf-mscorefonts-installer

For specific fonts, copy the ``.ttf`` (or ``.otf``) files into the folder
``/usr/local/share/fonts/custom/`` as root, and run the following command ::

    fc-cache

For more information, check out Ubuntu documentation.


Custom colors in public document OpenOffice template
----------------------------------------------------

Trek export geometries are translucid red by default. In order to control the
apparence of objects in public trek exports, use the following setting :

::

    MAP_STYLES['print']['path'] = {'weight': 3}

See *Leaflet* reference documentation for detail about layers apparence.


Custom logos
------------

You might also need to deploy logo images in the following places :

* ``var/conf/extra_static/images/favicon.png``
* ``var/conf/extra_static/images/logo-login.png``
* ``var/conf/extra_static/images/logo-header.png``


Share services between several Geotrek instances
------------------------------------------------

As explained :ref:`in the design section <design-section>`, *Geotrek* relies
on several services. They are generic and reusable, and can thus be shared
between several instances, in order to save system resources for example.

A simple way to achieve this is to install one instance with everything
as usual (*standalone*), and plug the other instances on its underlying services.


Database
~~~~~~~~

Geotrek stack come with its own database within its docker-compose.yml file

You can use own external postgis enabled database by adjust your settings in ``.env``

Then delete postgres section in docker-compose.yml


Capture and conversion
~~~~~~~~~~~~~~~~~~~~~~
If you want to use external services,

In ``.env``, add following variables:

.. code-block :: bash

    CAPTURE_HOST=x.x.x.x
    CAPTURE_PORT=XX
    CONVERSION_HOST=x.x.x.x
    CONVERSION_PORT=XX

Then, you can delete all screamshotter and convertit references in docker-compose.yml


Shutdown useless services
~~~~~~~~~~~~~~~~~~~~~~~~~

Now that your instances point the shared server. You can shutdown the useless
services on each instance.

Start by stopping everything :

::

    sudo systemctl stop geotrek


Control number of workers and request timeouts
----------------------------------------------

By default, the application runs on 4 processes, and timeouts after 30 seconds.

To control those values, edit and fix your docker-compose.yml file in web and api section

::

To know how many workers you should set, please refer to `gunicorn documentation <http://gunicorn-docs.readthedocs.org/en/latest/design.html#how-many-workers>`_.
