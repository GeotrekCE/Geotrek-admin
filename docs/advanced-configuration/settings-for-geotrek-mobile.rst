.. _settings-for-geotrek-mobile:

============================
Settings for Geotrek-mobile
============================

SYNC_MOBILE_ROOT
-----------------

  Path on your server where the datas for mobile will be saved.

    Example::

        SYNC_MOBILE_ROOT = os.path.join(VAR_DIR, 'mobile')

.. note:: 
  - If you want to modify it, do not forget to import os at the top of the file.
  - Check `import Python <https://docs.python.org/3/reference/import.html>`_ , if you need any information

SYNC_MOBILE_OPTIONS
--------------------

  Options of the sync_mobile command.

    Example::

        SYNC_MOBILE_OPTIONS = {'skip_tiles': False}

    Default::

        True

MOBILE_NUMBER_PICTURES_SYNC
----------------------------

  Number max of pictures that will be displayed and synchronized for each object (trek, POI, etc.) in the mobile app.

    Example::

        MOBILE_NUMBER_PICTURES_SYNC = 3

MOBILE_TILES_URL
-----------------

  URL's Tiles used for the mobile.

    Example with OpenTopoMap::

        MOBILE_TILES_URL = ['https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png']

    Example with IGN::

        MOBILE_TILES_URL = ['https://data.geopf.fr/wmts?SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0&LAYER=GEOGRAPHICALGRIDSYSTEMS.PLANIGNV2&STYLE=normal&FORMAT=image/png&TILEMATRIXSET=PM&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}']

MOBILE_LENGTH_INTERVALS
-------------------------

  Intervals of the mobile for the length filter.

    Example::

        MOBILE_LENGTH_INTERVALS =  [
        {"id": 1, "name": "< 10 km", "interval": [0, 9999]},
        {"id": 2, "name": "10 - 30", "interval": [9999, 29999]},
        {"id": 3, "name": "30 - 50", "interval": [30000, 50000]},
        {"id": 4, "name": "> 50 km", "interval": [50000, 999999]}
        ]

.. note:: 
  - Interval key is in meters.
  - You can add new intervals

MOBILE_ASCENT_INTERVALS
------------------------

  Intervals of the mobile for the ascent filter.

    Example::

        MOBILE_ASCENT_INTERVALS = [
        {"id": 1, "name": "< 300 m", "interval": [0, 299]},
        {"id": 2, "name": "300 - 600", "interval": [300, 599]},
        {"id": 3, "name": "600 - 1000", "interval": [600, 999]},
        {"id": 4, "name": "> 1000 m", "interval": [1000, 9999]}
        ]

.. note:: 
  Do the same as above

MOBILE_DURATION_INTERVALS
---------------------------

  Intervals of the mobile for the duration filter.

    Example::

        MOBILE_DURATION_INTERVALS = [
        {"id": 1, "name": "< 1 heure", "interval": [0, 1]},
        {"id": 2, "name": "1h - 2h30", "interval": [1, 2.5]},
        {"id": 3, "name": "2h30 - 5h", "interval": [2.5, 5]},
        {"id": 4, "name": "5h - 9h", "interval": [5, 9]},
        {"id": 5, "name": "> 9h", "interval": [9, 9999999]}
        ]

.. note:: 
  Check ``MOBILE_LENGTH_INTERVALS`` section to use it, here interval correspond to 1 unit of hour

ENABLED_MOBILE_FILTERS
-----------------------

  List of all the filters enabled on mobile.

    Example::

        ENABLED_MOBILE_FILTERS = [
        'practice',
        'difficulty',
        'duration',
        'ascent',
        'length',
        'themes',
        'route',
        'districts',
        'cities',
        'accessibilities',
        ]

.. note:: 
  Remove any of the filters if you don't want one of them. It's useless to add other one.

