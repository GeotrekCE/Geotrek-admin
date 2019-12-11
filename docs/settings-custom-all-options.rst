===============
Global Settings
===============

|

**Options before install**
==========================

**Spatial reference identifier**
::

    SRID = 2154

Spatial reference identifier of your database. 2154 is RGF93 / Lambert-93 - France

   *It should not be change after any creation of geometries.*

   *Choose wisely with epsg.io for example*

**Spatial Extent**
::

    SPATIAL_EXTENT = (105000, 6150000, 1100000, 7150000)

Boundingbox of your project : corner bottom left xy, corner top right xy, corner top right xy

   *It should not be change after install*


**Dynamic segmentation**
::

    TREKKING_TOPOLOGY_ENABLED = True

Use dynamic segmentation or not.

   *Do not change it after install, or dump your database*

**First Structure**
::

    DEFAULT_STRUCTURE_NAME = "GEOTEAM"

Name for your default structure.

   *This one can be changed, except it's tricky.*

   * *First change the name in the admin (authent/structure),*
   * *Stop your instance admin.*
   * *Change in the settings*
   * *Re-run the server.*

**Translations**
::

   MODELTRANSLATION_LANGUAGES = ('en', 'fr', 'it', 'es')

Languages of your project. It will be used to generate fields for translations. (ex: description_fr, description_en)

   *You won't be able to change it easily, avoid to add any languages and do not remove any.*

**Options admin**
=================
**Map config**
::

    LEAFLET_CONFIG['TILES'] = [
        ('Scan', '//wxs.ign.fr/<key>/wmts?LAYER=GEOGRAPHICALGRIDSYSTEMS.MAPS.SCAN-EXPRESS.STANDARD&EXCEPTIONS=image/jpeg&FORMAT=image/jpeg&SERVICE=WMTS&VERSION=1.0.0&REQUEST=GetTile&STYLE=normal&TILEMATRIXSET=PM&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}',
         '&copy; IGN - GeoPortail'),
        ('Ortho', '//wxs.ign.fr/<key>/wmts?LAYER=ORTHOIMAGERY.ORTHOPHOTOS&EXCEPTIONS=image/jpeg&FORMAT=image/jpeg&SERVICE=WMTS&VERSION=1.0.0&REQUEST=GetTile&STYLE=normal&TILEMATRIXSET=PM&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}',
         '&copy; IGN - GeoPortail'),
        ('Cadastre', '//wxs.ign.fr/<key>/wmts?LAYER=CADASTRALPARCELS.PARCELS&EXCEPTIONS=image/jpeg&FORMAT=image/png&SERVICE=WMTS&VERSION=1.0.0&REQUEST=GetTile&STYLE=normal&TILEMATRIXSET=PM&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}',
         '&copy; IGN - GeoPortail'),
        ('OSM', 'http://{s}.tile.osm.org/{z}/{x}/{y}.png', '&copy; OSM contributors'),
    ]

    LEAFLET_CONFIG['OVERLAYS'] = [
        ('Cadastre',
         '//wxs.ign.fr/<key>/wmts?LAYER=CADASTRALPARCELS.PARCELS&EXCEPTIONS=text/xml&FORMAT=image/png&SERVICE=WMTS&VERSION=1.0.0&REQUEST=GetTile&STYLE=bdparcellaire_o&TILEMATRIXSET=PM&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}',
         '&copy; IGN - GeoPortail'),
    ]

Configuration of the tiles.

    *If you want to change it,*
    *Change the array like that :*

    ::

        LEAFLET_CONFIG['TILES'] = [('NAME_OF_TILE', 'URL', 'COPYRIGHT'), ...]

    *It's the same for the overlay but use only transparent tiles*

|

::

    LEAFLET_CONFIG['MAX_ZOOM'] = 19

You can define the max_zoom the user can zoom for all tiles.

    *It can be interesting when your tiles can't go to this zoom. For example opentopomap.*

**Enable Apps**
::

    FLATPAGES_ENABLED = True

Show Flatpages on menu or not. Flatpages are used in Geotrek Rando.

|

::

    TOURISM_ENABLED = True

Show TouristicContents and TouristicEvents on menu or not.

|

::

    TRAIL_MODEL_ENABLED = True

Show Trails on menu or not.

|

::

    LANDEDGE_MODEL_ENABLED = True

Show land on menu or not.

|

::

   LAND_BBOX_CITIES_ENABLED = True
   LAND_BBOX_DISTRICTS_ENABLED = True
   LAND_BBOX_AREAS_ENABLED = False

Show filter bbox by zoning.

.. image:: images/options/zoning_bboxs.png

**Translations**
::

    LANGUAGE_CODE = 'fr'

Language of your interface.

**Geographical CRUD**
::

    PATH_SNAPPING_DISTANCE = 2.0

Minimum distance to merge 2 paths in unit of SRID

    *Change the distance. Better to keep it like this. Not used when TREKKING_TOPOLOGY_ENABLED = True*

::

    SNAP_DISTANCE = 30

Distance of snapping for the cursor in pixels on map leaflet.


::

    PATH_MERGE_SNAPPING_DISTANCE = 2

Minimum distance to merge 2 paths.

    *Change the distance. Should be higher or the same as PATH_SNAPPING_DISTANCE*

    *Used when TREKKING_TOPOLOGY_ENABLED = True*

::

    MAP_STYLES = {'path': {'weight': 2, 'opacity': 1.0, 'color': '#FF4800'},
                  'draftpath': {'weight': 5, 'opacity': 1, 'color': 'yellow', 'dashArray': '8, 8'},
                  'city': {'weight': 4, 'color': 'orange', 'opacity': 0.3, 'fillOpacity': 0.0},
                  'district': {'weight': 6, 'color': 'orange', 'opacity': 0.3, 'fillOpacity': 0.0, 'dashArray': '12, 12'},
                  'restrictedarea': {'weight': 2, 'color': 'red', 'opacity': 0.5, 'fillOpacity': 0.5},
                  'land': {'weight': 4, 'color': 'red', 'opacity': 1.0},
                  'physical': {'weight': 6, 'color': 'red', 'opacity': 1.0},
                  'competence': {'weight': 4, 'color': 'red', 'opacity': 1.0},
                  'workmanagement': {'weight': 4, 'color': 'red', 'opacity': 1.0},
                  'signagemanagement': {'weight': 5, 'color': 'red', 'opacity': 1.0},
                  'print': {'path': {'weight': 1},
                            'trek': {'color': '#FF3300', 'weight': 7, 'opacity': 0.5,
                                     'arrowColor': 'black', 'arrowSize': 10},}
                  }

Color of the different layers on the map

    *To change any map_style do as following :*

    ::

        MAP_STYLES['path'] = {'weigth': 2, 'opacity': 2.0, 'color': 'yellow'}*
        MAP_STYLES['city']['opacity'] = 0.8*

    *For color : use color picker for example*

|

::

    COLORS_POOL = {'land': ['#f37e79', '#7998f3', '#bbf379', '#f379df', '#f3bf79', '#9c79f3', '#7af379'],
                   'physical': ['#f3799d', '#79c1f3', '#e4f379', '#de79f3', '#79f3ba', '#f39779', '#797ff3'],
                   'competence': ['#a2f379', '#f379c6', '#79e9f3', '#f3d979', '#b579f3', '#79f392', '#f37984'],
                   'signagemanagement': ['#79a8f3', '#cbf379', '#f379ee', '#79f3e3', '#79f3d3'],
                   'workmanagement': ['#79a8f3', '#cbf379', '#f379ee', '#79f3e3', '#79f3d3'],
                   'restrictedarea': ['plum', 'violet', 'deeppink', 'orchid',
                                      'darkviolet', 'lightcoral', 'palevioletred',
                                      'MediumVioletRed', 'MediumOrchid', 'Magenta',
                                      'LightSalmon', 'HotPink', 'Fuchsia']}

Color of the different layers on the top right for landing.

    * For land, physical, competence, signagemanagement, workmanagement should have 5 values.
    * For restricted Area : add as many color as your number of restricted area type

    *To change any map_style do as following :*

    ::

        COLORS_POOL['restrictedarea'] = ['plum', 'violet', 'yellow', 'red', '#79a8f3']
        MAP_STYLES['city']['opacity'] = 0.8*

    *For color : use color picker for example*

|

::

    TREK_POINTS_OF_REFERENCE_ENABLED = True

Points of reference are enabled on form of treks.

|

::

    TOPOLOGY_STATIC_OFFSETS = {'land': -5, 'physical': 0, 'competence': 5, 'signagemanagement': -10, 'workmanagement': 10}

Land objects are added on other objects (path for example) with offset, avoiding overlay.

    *You should not change it to avoid overlay except if you want to have more overlay.*
    *You can do for example for :*

    ::

        TOPOLOGY_STATIC_OFFSETS = {'land': -7, 'physical': 0, 'competence': 7, 'signagemanagement': -14, 'workmanagement': 14}

|

::

    ALTIMETRIC_PROFILE_PRECISION = 25  # Sampling precision in meters
    ALTIMETRIC_PROFILE_AVERAGE = 2  # nb of points for altimetry moving average
    ALTIMETRIC_PROFILE_STEP = 1  # Step min precision for positive / negative altimetry gain
    ALTIMETRIC_PROFILE_BACKGROUND = 'white'
    ALTIMETRIC_PROFILE_COLOR = '#F77E00'
    ALTIMETRIC_PROFILE_HEIGHT = 400
    ALTIMETRIC_PROFILE_WIDTH = 800
    ALTIMETRIC_PROFILE_FONTSIZE = 25
    ALTIMETRIC_PROFILE_FONT = 'ubuntu'
    ALTIMETRIC_PROFILE_MIN_YSCALE = 1200  # Minimum y scale (in meters)
    ALTIMETRIC_AREA_MAX_RESOLUTION = 150  # Maximum number of points (by width/height)
    ALTIMETRIC_AREA_MARGIN = 0.15

All settings used for generate altimetric profile.

    *All this settings can be modify but you need to check the result every time*

    *The one modified most of the time is ALTIMETRIC_PROFILE_COLOR*

**Signage and Blade**
::

    BLADE_CODE_TYPE = int

Type of the blade code (str or int)

    *It can be str or int.*

    *If you have an integer code : int*

    *If you have an string code : str*

|

::

    BLADE_CODE_FORMAT = "{signagecode}-{bladenumber}"

Correspond of the format of blades. Show N3-1 for the blade 1 of the signage N3.

    *If you want to change : move information under bracket*

    *You can also remove one element between bracket*

    *You can do for exemple :*
    *"CD99.{signagecode}.{bladenumber}"*

    *It will display : CD99.XIDNZEIU.01 (first blade of XIDNZEIU)*

    * *signagecode is the code of the signage*
    * *bladenumber is the number of the blade*

|

::

    LINE_CODE_FORMAT = "{signagecode}-{bladenumber}-{linenumber}"

Correspond of the format showed on export of lines. Used in csv of signage.

    *Similar with above*
    *You can do for example :*
    *"CD99.{signagecode}-{bladenumber}.{linenumber}"*

    *It will display : CD99.XIDNZEIU-01.02 (second line of the first blade of XIDNZEIU)*

    * *signagecode is the code of the signage*
    * *bladenumber is the number of the blade*
    * *linenumber is the number of the line*


**Screenshots**
::

    SHOW_SENSITIVE_AREAS_ON_MAP_SCREENSHOT = True
    SHOW_POIS_ON_MAP_SCREENSHOT = True
    SHOW_SERVICES_ON_MAP_SCREENSHOT = True
    SHOW_SIGNAGES_ON_MAP_SCREENSHOT = True
    SHOW_INFRASTRUCTURES_ON_MAP_SCREENSHOT = True

Show objects on maps of pdf

|

::

    MAP_CAPTURE_SIZE = 800

Size in px of the capture.

    *Be careful with your pdfs.*
    *If you change this value, pdfs will be rendered differently*


**Synchro Geotrek-Rando**
::

    SYNC_RANDO_ROOT = os.path.join(VAR_DIR, 'data')

Path on your server where the datas for rando website will be generated

    *if you want to modify it, do not forget to import os at the top of the file.*
    *Check* `import Python <https://docs.python.org/3/reference/import.html>`_ *, if you need any information*

::

    THUMBNAIL_COPYRIGHT_FORMAT = ""

Add a thumbnail on every picture for geotrek-rando


    *Example :*

    *"{title}-:-{author}-:-{legend}"*

    *Will display title of the picture, author*
    *and the legend :*
    *Puy de Dômes-:-Paul Paul-:-Beautiful sunrise on Puy de Dômes"*

|

::

    THUMBNAIL_COPYRIGHT_SIZE = 15

Size of the thumbnail.

|

::

    TOURISM_INTERSECTION_MARGIN = 500

Distance to which tourist contents, tourist events, treks, pois, services will be displayed

    *This distance can be changed by practice for treks in the admin.*

|

::

    DIVING_INTERSECTION_MARGIN = 500

Distance to which dives will be displayed.

|

::

    TREK_EXPORT_POI_LIST_LIMIT = 14

Limit of the number of pois on treks pdf.

    *14 is already a huge amount of POI, but it's possible to add more*

|

::

    TREK_EXPORT_INFORMATION_DESK_LIST_LIMIT = 2

Limit of the number of information desks on treks pdf.

    *You can put -1 if you want all the information desks*

|

::

    SPLIT_TREKS_CATEGORIES_BY_PRACTICE = False

On the Rando web site, treks practices will be displayed separately

    *Field order for each practices in admin will be take in account*

|

::

    SPLIT_TREKS_CATEGORIES_BY_ACCESSIBILITY = False

On the Rando web site, accessibilites will be displayed separately

|

::

    SPLIT_TREKS_CATEGORIES_BY_ITINERANCY = False

On the Rando web site, if a trek has a children it will be displayed separately

|

::

    SPLIT_DIVES_CATEGORIES_BY_PRACTICE = True

On the Rando web site, dives practices will be displayed separately

|

::

    HIDE_PUBLISHED_TREKS_IN_TOPOLOGIES = False

On the 'Rando' web site, treks near other are hide

|

::

    SYNC_RANDO_OPTIONS = {}

Options of the sync_rando command in Geotrek-admin interface.

|

::

    TREK_WITH_POIS_PICTURES = False

It enables correlated pictures on Gotrek-Rando to be displayed in the slideshow

|

::

    PRIMARY_COLOR = "#7b8c12"

Primary color of your pdf
    *check : "color picker"*

|

::

    ONLY_EXTERNAL_PUBLIC_PDF = False

On rando web site, only pdf imported with filetype "Topoguide"
will be used and not autogenerated.

|

::

    TREK_CATEGORY_ORDER = 1
    ITINERANCY_CATEGORY_ORDER = 2
    DIVE_CATEGORY_ORDER = 10
    TOURISTIC_EVENT_CATEGORY_ORDER = 99

Order of all the objects without practices on 'Rando' web site

    *All the settings about order are the order inside rando web site.*

    *Practices of diving, treks and categories of touristic contents are taken in account*

|

**Synchro Geotrek-Mobile**
::

    SYNC_MOBILE_ROOT = os.path.join(VAR_DIR, 'mobile')

Path on your server wehre the datas for mobile

    *if you want to modify it, do not forget to import os at the top of the file.*
    *Check* `import Python <https://docs.python.org/3/reference/import.html>`_ *, if you need any information*

|

::

    SYNC_MOBILE_OPTIONS = {'skip_tiles': False}

Options of the sync_mobile command

|

::

    MOBILE_TILES_URL = ['https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png']

URL's Tiles used for the mobile.

    *Change for ign :*

    ::

        MOBILE_TILES_URL = ['https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png']

|

::

    MOBILE_LENGTH_INTERVALS =  [
        {"id": 1, "name": "< 10 km", "interval": [0, 9999]},
        {"id": 2, "name": "10 - 30", "interval": [9999, 29999]},
        {"id": 3, "name": "30 - 50", "interval": [30000, 50000]},
        {"id": 4, "name": "> 50 km", "interval": [50000, 999999]}
    ]

Intervals of the mobile for the length filter

    *Interval's key is in meters.*
    *You can add new intervals*

    ::

        MOBILE_LENGTH_INTERVALS =  [
            {"id": 1, "name": "< 10 km", "interval": [0, 9999]},
            {"id": 2, "name": "10 - 30 km", "interval": [9999, 29999]},
            {"id": 3, "name": "30 - 50 km", "interval": [30000, 50000]},
            {"id": 4, "name": "50 - 80 km", "interval": [50000, 80000]}
            {"id": 5, "name": "> 80 km", "interval": [80000, 999999]}
        ]

|

::

    MOBILE_ASCENT_INTERVALS = [
        {"id": 1, "name": "< 300 m", "interval": [0, 299]},
        {"id": 2, "name": "300 - 600", "interval": [300, 599]},
        {"id": 3, "name": "600 - 1000", "interval": [600, 999]},
        {"id": 4, "name": "> 1000 m", "interval": [1000, 9999]}
    ]

Intervals of the mobile for the ascent filter

    *Do the same as above*

::

    MOBILE_DURATION_INTERVALS = [
        {"id": 1, "name": "< 1 heure", "interval": [0, 1]},
        {"id": 2, "name": "1h - 2h30", "interval": [1, 2.5]},
        {"id": 3, "name": "2h30 - 5h", "interval": [2.5, 5]},
        {"id": 4, "name": "5h - 9h", "interval": [5, 9]},
        {"id": 5, "name": "> 9h", "interval": [9, 9999999]}
    ]

Intervals of the mobile for the duration filter

    *Check MOBILE_LENGTH_INTERVALS comment to use it, here interval correspond to 1 unit of hour*

|

::

    ENABLED_MOBILE_FILTERS = [
        'practice',
        'difficulty',
        'durations',
        'ascent',
        'lengths',
        'themes',
        'route',
        'districts',
        'cities',
        'accessibilities',
    ]

List of all the filters enabled on mobile.

    *Remove any of the filters if you don't want one of them. It's useless to add other one.*



**Other settings**
::

    SEND_REPORT_ACK = True

If false, no mail will be sent to the sender of any feedback on Rando web site
