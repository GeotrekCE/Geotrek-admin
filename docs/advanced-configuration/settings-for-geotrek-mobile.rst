.. _settings-for-geotrek-mobile:

============================
Settings for Geotrek-mobile
============================

.. info::
  
  For a complete list of available parameters, refer to the default values in `geotrek/settings/base.py <https://github.com/GeotrekCE/Geotrek-admin/blob/master/geotrek/settings/base.py>`_.

Sync mobile root
-----------------

Defines the path on your server where mobile data will be saved.

Example::

    SYNC_MOBILE_ROOT = os.path.join(VAR_DIR, 'mobile')

.. note:: 
  - If modifying this setting, ensure to import ``os`` at the top of the file.
  - See the `Python import reference <https://docs.python.org/3/reference/import.html>`_ for details.

Sync mobile options 
--------------------

Options of the sync_mobile command.

Here are the options you can use with this command : ``portal``, ``languages``, ``skip_tiles``

.. md-tab-set::
    :name: sync-mobile-options-tabs

    .. md-tab-item:: Default configuration

         .. code-block:: python
    
                SYNC_MOBILE_OPTIONS = {'skip_tiles': False}

    .. md-tab-item:: Example

         .. code-block:: python
    
                SYNC_MOBILE_OPTIONS = {'skip_tiles': True}

Mobile number pictures sync 
----------------------------

Defines the maximum number of pictures synchronized and displayed for each object (trek, POI, etc.) in the mobile app.

.. md-tab-set::
    :name: sync-mobile-pictures-tabs

    .. md-tab-item:: Default configuration

         .. code-block:: python
    
                MOBILE_NUMBER_PICTURES_SYNC = 3

    .. md-tab-item:: Example

         .. code-block:: python
    
                MOBILE_NUMBER_PICTURES_SYNC = 5

Mobile tile URL
-----------------

Defines the tile URLs used for the mobile application.

.. md-tab-set::
    :name: mobile-tile-url-tabs

    .. md-tab-item:: Example with OpenTopoMap

         .. code-block:: python
    
                MOBILE_TILES_URL = ['https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png']

    .. md-tab-item:: Example with IGN

         .. code-block:: python
    
                MOBILE_TILES_URL = ['https://data.geopf.fr/wmts?SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0&LAYER=GEOGRAPHICALGRIDSYSTEMS.PLANIGNV2&STYLE=normal&FORMAT=image/png&TILEMATRIXSET=PM&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}']

Mobile length intervals 
-------------------------

Defines length intervals for filtering in the mobile app.

.. md-tab-set::
    :name: mobile-length-intervals-tabs

    .. md-tab-item:: Default configuration

         .. code-block:: python
    
                    MOBILE_LENGTH_INTERVALS =  [
                      {"id": 1, "name": "< 10 km", "interval": [0, 9999]},
                      {"id": 2, "name": "10 - 30", "interval": [9999, 29999]},
                      {"id": 3, "name": "30 - 50", "interval": [30000, 50000]},
                      {"id": 4, "name": "> 50 km", "interval": [50000, 999999]}
                      ]

    .. md-tab-item:: Example

         .. code-block:: python
    
                    MOBILE_LENGTH_INTERVALS =  [
                      {"id": 1, "name": "< 5 km", "interval": [0, 4999]},
                      {"id": 2, "name": "5 - 10", "interval": [5000, 9999]},
                      {"id": 3, "name": "10 - 50", "interval": [10000, 49999]},
                      {"id": 4, "name": "> 50 km", "interval": [50000, 999999]}
                      ]

.. note:: 
  - The ``interval`` values are in meters.
  - You can define custom intervals.

Mobile ascent intervals  
------------------------

Defines ascent intervals for filtering in the mobile app.

.. md-tab-set::
    :name: mobile-ascent-intervals-tabs

    .. md-tab-item:: Default configuration

         .. code-block:: python
    
                    MOBILE_ASCENT_INTERVALS = [
                      {"id": 1, "name": "< 300 m", "interval": [0, 299]},
                      {"id": 2, "name": "300 - 600", "interval": [300, 599]},
                      {"id": 3, "name": "600 - 1000", "interval": [600, 999]},
                      {"id": 4, "name": "> 1000 m", "interval": [1000, 9999]}
                      ]

    .. md-tab-item:: Example

         .. code-block:: python
    
                    MOBILE_ASCENT_INTERVALS = [
                      {"id": 1, "name": "< 100 m", "interval": [0, 99]},
                      {"id": 2, "name": "100 - 300", "interval": [99, 299]},
                      {"id": 3, "name": "300 - 600", "interval": [300, 599]},
                      {"id": 4, "name": "> 600 m", "interval": [600, 9999]}
                      ]

.. note:: 
  - The ``interval`` values are in meters.
  - You can define custom intervals.

Mobile duration intervals  
---------------------------

Defines duration intervals for filtering in the mobile app.

.. md-tab-set::
    :name: mobile-duration-intervals-tabs

    .. md-tab-item:: Default configuration

            .. code-block:: python
    
                    MOBILE_DURATION_INTERVALS = [
                      {"id": 1, "name": "< 1 heure", "interval": [0, 1]},
                      {"id": 2, "name": "1h - 2h30", "interval": [1, 2.5]},
                      {"id": 3, "name": "2h30 - 5h", "interval": [2.5, 5]},
                      {"id": 4, "name": "5h - 9h", "interval": [5, 9]},
                      {"id": 5, "name": "> 9h", "interval": [9, 9999999]}
                      ]

    .. md-tab-item:: Example

         .. code-block:: python
    
                    MOBILE_DURATION_INTERVALS = [
                      {"id": 1, "name": "< 1 heure", "interval": [0, 1]},
                      {"id": 2, "name": "1h - 3h30", "interval": [1, 3.5]},
                      {"id": 3, "name": "3h30 - 5h", "interval": [3.5, 5]},
                      {"id": 4, "name": "5h - 10h", "interval": [5, 10]},
                      {"id": 5, "name": "> 10h", "interval": [10, 9999999]}
                      ]

.. note:: 
  The intervals represent hours.

Enabled mobile filters  
-----------------------

Defines the list of enabled filters in the mobile app.

.. md-tab-set::
    :name: enabled-mobile-filters-tabs

    .. md-tab-item:: Default configuration

            .. code-block:: python
    
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

    .. md-tab-item:: Example

         .. code-block:: python
    
                    ENABLED_MOBILE_FILTERS = [
                    'practice',
                    'difficulty',
                    'duration',
                    'length',
                    'themes',
                    'route',
                    'accessibilities',
                    ]


