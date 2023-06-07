
==================
Settings reference
==================

Basic settings
--------------

**Spatial reference identifier**

::

    SRID = 2154

Spatial reference identifier of your database. Default 2154 is RGF93 / Lambert-93 - France

*It should not be change after any creation of geometries.*

*Choose wisely with epsg.io for example*


**Default Structure**

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

Advanced settings
-----------------

**Spatial Extent**

::

    SPATIAL_EXTENT = (105000, 6150000, 1100000, 7150000)

Boundingbox of your project : x minimum , y minimum , x max, y max

::

        4 ^
          |
    1     |     3
    <-----+----->
          |
          |
        2 v

*If you extend spatial extent, don't forget to load a new DEM that covers all the zone.*
*If you shrink spatial extent, be sure there is no element in the removed zone or you will no more be able to see and edit it.*

**API**

::

    API_IS_PUBLIC = True

Choose if you want the API V2 to be available for everyone without authentication. This API provides access to promotion content (Treks, POIs, Touristic Contents ...). Set to False if Geotrek is intended to be used only for managing content and not promoting them.
Note that this setting does not impact the Path endpoints, which means that the Paths informations will always need authentication to be display in the API, regardless of this setting.

**Dynamic segmentation**

::

    TREKKING_TOPOLOGY_ENABLED = True

Use dynamic segmentation or not.

`Dynamic segmentation <https://geotrek.readthedocs.io/en/latest/usage/editing-objects.html#segmentation-dynamique>`_ is used by default when installing Geotrek-admin.

With this mode, linear objects are built and stored related to paths.

Without this mode, linear geometry of objects is built and stored as an independent geographic object without relation to paths.

So if you want to use Geotrek-admin without dynamic segmentation, set TREKKING_TOPOLOGY_ENABLED to false after installation.

Do not change it again to true after setting it to false.

**Map configuration**

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
    *Change the array like that:*

    ::

        LEAFLET_CONFIG['TILES'] = [('NAME_OF_TILE', 'URL', 'COPYRIGHT'), ...]

    *It's the same for the overlay but use only transparent tiles.*

|

::

    LEAFLET_CONFIG['MAX_ZOOM'] = 19

You can define the max_zoom the user can zoom for all tiles.

    *It can be interesting when your tiles can't go to a zoom. For example OpenTopoMap is 17.*

**Enable Apps**

::

    FLATPAGES_ENABLED = True

Show Flatpages on menu or not. Flatpages are used in Geotrek-rando.

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

.. image:: /images/options/zoning_bboxs.png


|

::

   ACCESSIBILITY_ATTACHMENTS_ENABLED = True

Show or not the accessibility menu for attachments

**Translations**

::

    LANGUAGE_CODE = 'fr'

Language of your interface.

**Geographical CRUD**

::

    PATH_SNAPPING_DISTANCE = 2.0

Minimum distance to merge 2 paths in unit of SRID

    *Change the distance. Better to keep it like this. Not used when ``TREKKING_TOPOLOGY_ENABLED = True``.*

::

    SNAP_DISTANCE = 30

Distance of snapping for the cursor in pixels on Leaflet map.


::

    PATH_MERGE_SNAPPING_DISTANCE = 2

Minimum distance to merge 2 paths.

    *Change the distance. Should be higher or the same as PATH_SNAPPING_DISTANCE*

    *Used when TREKKING_TOPOLOGY_ENABLED = True*

::

    MAPENTITY_CONFIG['MAP_STYLES'] = {
        'path': {'weight': 2, 'opacity': 1.0, 'color': '#FF4800'},
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

    *To change any map_style do as following:*

    ::

        MAPENTITY_CONFIG['MAP_STYLES']['path'] = {'weigth': 2, 'opacity': 2.0, 'color': 'yellow'}*
        MAPENTITY_CONFIG['MAP_STYLES']['city']['opacity'] = 0.8*

    *For color: use color picker for example*

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
    * For restricted Area: add as many color as your number of restricted area type

    *To change any map_style do as following :*

    ::

        COLORS_POOL['restrictedarea'] = ['plum', 'violet', 'yellow', 'red', '#79a8f3']
        MAPENTITY_CONFIG['MAP_STYLES']['city']['opacity'] = 0.8*

    *For color: use color picker for example*

|

::

    TREK_POINTS_OF_REFERENCE_ENABLED = True

Points of reference are enabled on form of treks.

|

::

    OUTDOOR_COURSE_POINTS_OF_REFERENCE_ENABLED = True

Points of reference are enabled on form of otudoor courses.

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

All settings used to generate altimetric profile.

    *All these settings can be modified but you need to check the result every time*

    *The only one modified most of the time is ALTIMETRIC_PROFILE_COLOR*

**Signage and Blade**

``BLADE_ENABLED`` and ``LINE_ENABLED`` settings (default to ``True``) allow to enable or disable blades and lines submodules.

``DIRECTION_ON_LINES_ENABLED`` setting (default to ``False``) allow to have the `direction` field on lines instead of blades.

::

    BLADE_CODE_TYPE = int

Type of the blade code (str or int)

    *It can be str or int.*

    *If you have an integer code : int*

    *If you have an string code : str*

|

::

    BLADE_CODE_FORMAT = "{signagecode}-{bladenumber}"

Correspond to the format of blades. Show N3-1 for the blade 1 of the signage N3.

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

Correspond to the format used in export of lines. Used in csv of signage.

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

Show objects on maps of PDF

|

::

    MAP_CAPTURE_SIZE = 800

Size in pixels of the capture.

    *Be careful with your pdfs.*
    *If you change this value, pdfs will be rendered differently*


**Synchro Geotrek-rando**

::

    SYNC_RANDO_ROOT = os.path.join(VAR_DIR, 'data')

Path on your server where the data for Geotrek-rando website will be generated

    *If you want to modify it, do not forget to import os at the top of the file.*
    *Check* `import Python <https://docs.python.org/3/reference/import.html>`_ *, if you need any information*

::

    THUMBNAIL_COPYRIGHT_FORMAT = ""

Add a thumbnail on every picture for Geotrek-rando


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

On the Geotrek-rando v2 website, treks practices will be displayed separately

    *Field order for each practices in admin will be take in account*

|

::

    SPLIT_TREKS_CATEGORIES_BY_ACCESSIBILITY = False

On the Geotrek-rando v2 website, accessibilites will be displayed separately

|

::

    SPLIT_TREKS_CATEGORIES_BY_ITINERANCY = False

On the Geotrek-rando v2 website, if a trek has a children it will be displayed separately

|

::

    SPLIT_DIVES_CATEGORIES_BY_PRACTICE = True

On the Geotrek-rando v2 website, dives practices will be displayed separately

|

::

    HIDE_PUBLISHED_TREKS_IN_TOPOLOGIES = False

On the Geotrek-rando v2 website, treks near other are hidden

|

::

    SYNC_RANDO_OPTIONS = {}

Options of the sync_rando command in Geotrek-admin interface.

|

::

    TREK_WITH_POIS_PICTURES = False

It enables correlated pictures on Gotrek-rando v2 to be displayed in the slideshow

|

::

    PRIMARY_COLOR = "#7b8c12"

Primary color of your PDF
    *check : "color picker"*

|

::

    ONLY_EXTERNAL_PUBLIC_PDF = False

On Geotrek-rando v2 website, only PDF imported with filetype "Topoguide"
will be used and not autogenerated.

|

::

    TREK_CATEGORY_ORDER = 1
    ITINERANCY_CATEGORY_ORDER = 2
    DIVE_CATEGORY_ORDER = 10
    TOURISTIC_EVENT_CATEGORY_ORDER = 99

Order of all the objects without practices on Geotrek-rando website

    *All the settings about order are the order inside Geotrek-rando website.*

    *Practices of diving, treks and categories of touristic contents are taken in account*

|

**Synchro Geotrek-mobile**

::

    SYNC_MOBILE_ROOT = os.path.join(VAR_DIR, 'mobile')

Path on your server where the datas for mobile will be saved

    *If you want to modify it, do not forget to import os at the top of the file.*
    *Check* `import Python <https://docs.python.org/3/reference/import.html>`_ *, if you need any information*

|

::

    SYNC_MOBILE_OPTIONS = {'skip_tiles': False}

Options of the sync_mobile command

|

::

    MOBILE_NUMBER_PICTURES_SYNC = 3

Number max of pictures that will be displayed and synchronized for each object (trek, poi, etc.) in the mobile app.

|

::

    MOBILE_TILES_URL = ['https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png']

URL's Tiles used for the mobile.

    *Change for IGN:*

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

    *Interval key is in meters.*
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


|

**Custom columns available**

A (nearly?) exhaustive list of attributes available for display and export as columns in each module.

::

    COLUMNS_LISTS["path_view"] = [
        "length_2d",
        "valid",
        "structure",
        "visible",
        "min_elevation",
        "max_elevation",
        "date_update",
        "date_insert",
        "stake",
        "networks",
        "comments",
        "departure",
        "arrival",
        "comfort",
        "source",
        "usages",
        "draft",
        "trails",
        "uuid",
    ]
    COLUMNS_LISTS["trail_view"] = [
        "departure",
        "arrival",
        "category",
        "length",
        "structure",
        "min_elevation",
        "max_elevation",
        "date_update",
        "length_2d",
        "date_insert",
        "comments",
        "uuid",
    ]
    COLUMNS_LISTS["landedge_view"] = [
        "eid",
        "min_elevation",
        "max_elevation",
        "date_update",
        "length_2d",
        "date_insert",
        "owner",
        "agreement",
        "uuid",
    ]
    COLUMNS_LISTS["physicaledge_view"] = [
        "eid",
        "date_insert",
        "date_update",
        "length",
        "length_2d",
        "min_elevation",
        "max_elevation",
        "uuid",
    ]
    COLUMNS_LISTS["competenceedge_view"] = [
        "eid",
        "date_insert",
        "date_update",
        "length",
        "length_2d",
        "min_elevation",
        "max_elevation",
        "uuid",
    ]
    COLUMNS_LISTS["signagemanagementedge_export"] = [
        "eid",
        "date_insert",
        "date_update",
        "length",
        "length_2d",
        "min_elevation",
        "max_elevation",
        "uuid",
        "provider"
    ]
    COLUMNS_LISTS["workmanagementedge_export"] = [
        "eid",
        "date_insert",
        "date_update",
        "length",
        "length_2d",
        "min_elevation",
        "max_elevation",
        "uuid",
    ]
    COLUMNS_LISTS["infrastructure_view"] = [
        "condition",
        "cities",
        "structure",
        "type",
        "description",
        "accessibility",
        "date_update",
        "date_insert",
        "implantation_year",
        "usage_difficulty",
        "maintenance_difficulty",
        "published",
        "uuid",
        "eid",
        "provider",
        "access"
    ]
    COLUMNS_LISTS["signage_view"] = [
        "code",
        "type",
        "condition",
        "structure",
        "description",
        "date_update",
        "date_insert",
        "implantation_year",
        "printed_elevation",
        "coordinates",
        "sealing",
        "access",
        "manager",
        "published",
        "uuid",
    ]
    COLUMNS_LISTS["intervention_view"] = [
        "date",
        "type",
        "target",
        "status",
        "stake",
        "structure",
        "subcontracting",
        "status",
        "disorders",
        "length",
        "material_cost",
        "min_elevation",
        "max_elevation",
        "heliport_cost",
        "subcontract_cost",
        "date_update",
        "date_insert",
        "description",
    ]
    COLUMNS_LISTS["project_view"] = [
        "structure",
        "begin_year",
        "end_year",
        "constraint",
        "global_cost",
        "type",
        "date_update",
        "domain",
        "contractors",
        "project_owner",
        "project_manager",
        "founders",
        "date_insert",
        "comments",
    ]
    COLUMNS_LISTS["trek_view"] = [
        "structure",
        "departure",
        "arrival",
        "duration",
        "description_teaser",
        "description",
        "gear",
        "route",
        "difficulty",
        "ambiance",
        "access",
        "accessibility_infrastructure",
        "advised_parking",
        "parking_location",
        "public_transport",
        "themes",
        "practice",
        "min_elevation",
        "max_elevation",
        "length_2d",
        "date_update",
        "date_insert",
        "accessibilities",
        "accessibility_advice",
        "accessibility_covering",
        "accessibility_exposure",
        "accessibility_level",
        "accessibility_signage",
        "accessibility_slope",
        "accessibility_width",
        "ratings_description",
        "ratings",
        "points_reference",
        "source",
        "reservation_system",
        "reservation_id",
        "portal",
        "uuid",
        "eid",
        "eid2",
        "provider"
    ]
    COLUMNS_LISTS["poi_view"] = [
        "structure",
        "description",
        "type",
        "min_elevation",
        "date_update",
        "date_insert",
        "uuid",
    ]
    COLUMNS_LISTS["service_view"] = [
        "structure",
        "min_elevation",
        "type",
        "length_2d",
        "date_update",
        "date_insert",
        "uuid",
    ]
    COLUMNS_LISTS["dive_view"] = [
        "structure",
        "description_teaser",
        "description",
        "owner",
        "practice",
        "departure",
        "disabled_sport",
        "facilities",
        "difficulty",
        "levels",
        "depth",
        "advice",
        "themes",
        "source",
        "portal",
        "date_update",
        "date_insert",
    ]
    COLUMNS_LISTS["touristic_content_view"] = [
        "structure",
        "description_teaser",
        "description",
        "category",
        "contact",
        "email",
        "website",
        "practical_info",
        "accessibility",
        "label_accessibility",
        "type1",
        "type2",
        "source",
        "reservation_system",
        "reservation_id",
        "date_update",
        "date_insert",
        "uuid",
        "eid",
        "provider"
    ]
    COLUMNS_LISTS["touristic_event_view"] = [
        "structure",
        "themes",
        "description_teaser",
        "description",
        "meeting_point",
        "start_time",
        "end_time",
        "duration",
        "begin_date",
        "contact",
        "email",
        "website",
        "end_date",
        "organizer",
        "speaker",
        "type",
        "accessibility",
        "capacity",
        "portal",
        "source",
        "practical_info",
        "target_audience",
        "booking",
        "date_update",
        "date_insert",
        "uuid",
        "eid",
        "provider",
        "bookable",
        "cancelled",
        "cancellation_reason"
        "place",
        'preparation_duration',
        'intervention_duration',
    ]
    COLUMNS_LISTS["feedback_view"] = [
        "email",
        "comment",
        "activity",
        "category",
        "problem_magnitude",
        "status",
        "related_trek",
        "uuid",
        "eid",
        "external_eid",
        "locked",
        "origin"
        "date_update",
        "date_insert",
        "created_in_suricate",
        "last_updated_in_suricate",
        "assigned_user",
        "uses_timers"
    ]
    COLUMNS_LISTS["sensitivity_view"] = [
        "structure",
        "species",
        "published",
        "publication_date",
        "contact",
        "pretty_period",
        "category",
        "pretty_practices",
        "description",
        "date_update",
        "date_insert",
    ]
    COLUMNS_LISTS["outdoor_site_view"] = [
        "structure",
        "name",
        "practice",
        "description",
        "description_teaser",
        "ambiance",
        "advice",
        "accessibility",
        "period",
        "labels",
        "themes",
        "portal",
        "source",
        "information_desks",
        "web_links",
        "eid",
        "orientation",
        "wind",
        "ratings",
        "managers",
        "type",
        "description",
        "description_teaser",
        "ambiance",
        "period",
        "orientation",
        "wind",
        "labels",
        "themes",
        "portal",
        "source",
        "managers",
        "min_elevation",
        "date_insert",
        "date_update",
        "uuid",
    ]
    COLUMNS_LISTS["outdoor_course_view"] = [
        "structure",
        "name",
        "parent_sites",
        "description",
        "advice",
        "equipment",
        "accessibility",
        "eid",
        "height",
        "ratings",
        "gear",
        "duration"
        "ratings_description",
        "type",
        "points_reference",
        "uuid",
    ]
    COLUMNS_LISTS["path_export"] = [
        "structure",
        "valid",
        "visible",
        "name",
        "comments",
        "departure",
        "arrival",
        "comfort",
        "source",
        "stake",
        "usages",
        "networks",
        "date_insert",
        "date_update",
        "length_2d",
        "length",
        "ascent",
        "descent",
        "min_elevation",
        "max_elevation",
        "slope",
        "uuid",
    ]
    COLUMNS_LISTS["trail_export"] = [
        "structure",
        "name",
        "comments",
        "departure",
        "arrival",
        "category",
        "certifications",
        "date_insert",
        "date_update",
        "cities",
        "districts",
        "areas",
        "length",
        "ascent",
        "descent",
        "min_elevation",
        "max_elevation",
        "slope",
        "uuid",
    ]
    COLUMNS_LISTS["landedge_export"] = [
        "eid",
        "land_type",
        "owner",
        "agreement",
        "date_insert",
        "date_update",
        "cities",
        "districts",
        "areas",
        "length",
        "length_2d",
        "ascent",
        "descent",
        "min_elevation",
        "max_elevation",
        "slope",
        "uuid",
    ]
    COLUMNS_LISTS["physicaledge_export"] = [
        "eid",
        "physical_type",
        "date_insert",
        "date_update",
        "cities",
        "districts",
        "areas",
        "length",
        "length_2d",
        "ascent",
        "descent",
        "min_elevation",
        "max_elevation",
        "slope",
        "uuid",
    ]
    COLUMNS_LISTS["competenceedge_export"] = [
        "eid",
        "organization",
        "date_insert",
        "date_update",
        "cities",
        "districts",
        "areas",
        "length",
        "length_2d",
        "ascent",
        "descent",
        "min_elevation",
        "max_elevation",
        "slope",
        "uuid",
    ]
    COLUMNS_LISTS["signagemanagementedge_export"] = [
        "eid",
        "organization",
        "date_insert",
        "date_update",
        "cities",
        "districts",
        "areas",
        "length",
        "length_2d",
        "ascent",
        "descent",
        "min_elevation",
        "max_elevation",
        "slope",
        "uuid",
    ]
    COLUMNS_LISTS["workmanagementedge_export"] = [
        "eid",
        "organization",
        "date_insert",
        "date_update",
        "cities",
        "districts",
        "areas",
        "length",
        "length_2d",
        "ascent",
        "descent",
        "min_elevation",
        "max_elevation",
        "slope",
        "uuid",
    ]
    COLUMNS_LISTS["infrastructure_export"] = [
        "name",
        "type",
        "condition",
        "access",
        "description",
        "accessibility",
        "implantation_year",
        "published",
        "publication_date",
        "structure",
        "date_insert",
        "date_update",
        "cities",
        "districts",
        "areas",
        "ascent",
        "descent",
        "min_elevation",
        "max_elevation",
        "slope",
        "usage_difficulty",
        "maintenance_difficulty"
        "uuid",
        "eid",
        "provider"
    ]
    COLUMNS_LISTS["signage_export"] = [
        "structure",
        "name",
        "code",
        "type",
        "condition",
        "description",
        "implantation_year",
        "published",
        "date_insert",
        "date_update",
        "cities",
        "districts",
        "areas",
        "lat_value",
        "lng_value",
        "printed_elevation",
        "sealing",
        "access",
        "manager",
        "length",
        "ascent",
        "descent",
        "min_elevation",
        "max_elevation",
        "uuid",
        "eid",
        "provider"
    ]
    COLUMNS_LISTS["intervention_export"] = [
        "name",
        "date",
        "type",
        "target",
        "status",
        "stake",
        "disorders",
        "total_manday",
        "project",
        "subcontracting",
        "width",
        "height",
        "length",
        "area",
        "structure",
        "description",
        "date_insert",
        "date_update",
        "material_cost",
        "heliport_cost",
        "subcontract_cost",
        "total_cost_mandays",
        "total_cost",
        "cities",
        "districts",
        "areas",
        "length",
        "ascent",
        "descent",
        "min_elevation",
        "max_elevation",
        "slope",
    ]
    COLUMNS_LISTS["project_export"] = [
        "structure",
        "name",
        "period",
        "type",
        "domain",
        "constraint",
        "global_cost",
        "interventions",
        "interventions_total_cost",
        "comments",
        "contractors",
        "project_owner",
        "project_manager",
        "founders",
        "date_insert",
        "date_update",
        "cities",
        "districts",
        "areas",
    ]
    COLUMNS_LISTS["trek_export"] = [
        "eid",
        "eid2",
        "structure",
        "name",
        "departure",
        "arrival",
        "duration",
        "duration_pretty",
        "description",
        "description_teaser",
        "gear",
        "networks",
        "advice",
        "ambiance",
        "difficulty",
        "information_desks",
        "themes",
        "practice",
        "accessibilities",
        "accessibility_advice",
        "accessibility_covering",
        "accessibility_exposure",
        "accessibility_level",
        "accessibility_signage",
        "accessibility_slope",
        "accessibility_width",
        "ratings_description",
        "ratings",
        "access",
        "route",
        "public_transport",
        "advised_parking",
        "web_links",
        "labels",
        "accessibility_infrastructure",
        "parking_location",
        "points_reference",
        "related",
        "children",
        "parents",
        "pois",
        "review",
        "published",
        "publication_date",
        "date_insert",
        "date_update",
        "cities",
        "districts",
        "areas",
        "source",
        "portal",
        "length_2d",
        "length",
        "ascent",
        "descent",
        "min_elevation",
        "max_elevation",
        "slope",
        "uuid",
        "provider"
    ]
    COLUMNS_LISTS["poi_export"] = [
        "structure",
        "eid",
        "name",
        "type",
        "description",
        "treks",
        "review",
        "published",
        "publication_date",
        "structure",
        "date_insert",
        "date_update",
        "cities",
        "districts",
        "areas",
        "length",
        "ascent",
        "descent",
        "min_elevation",
        "max_elevation",
        "slope",
        "uuid",
    ]
    COLUMNS_LISTS["service_export"] = [
        "eid",
        "type",
        "length",
        "ascent",
        "descent",
        "min_elevation",
        "max_elevation",
        "slope",
        "uuid",
    ]
    COLUMNS_LISTS["dive_export"] = [
        "eid",
        "structure",
        "name",
        "departure",
        "description",
        "description_teaser",
        "advice",
        "difficulty",
        "levels",
        "themes",
        "practice",
        "disabled_sport",
        "published",
        "publication_date",
        "date_insert",
        "date_update",
        "areas",
        "source",
        "portal",
        "review",
        "uuid",
    ]
    COLUMNS_LISTS["touristic_content_export"] = [
        "structure",
        "eid",
        "name",
        "category",
        "type1",
        "type2",
        "description_teaser",
        "description",
        "themes",
        "contact",
        "email",
        "website",
        "practical_info",
        "accessibility",
        "label_accessibility",
        "review",
        "published",
        "publication_date",
        "source",
        "portal",
        "date_insert",
        "date_update",
        "cities",
        "districts",
        "areas",
        "approved",
        "uuid",
        "provider"
    ]
    COLUMNS_LISTS["touristic_event_export"] = [
        "structure",
        "eid",
        "name",
        "type",
        "description_teaser",
        "description",
        "themes",
        "begin_date",
        "end_date",
        "duration",
        "meeting_point",
        "start_time",
        "end_time",
        "contact",
        "email",
        "website",
        "organizer",
        "speaker",
        "accessibility",
        "capacity",
        "booking",
        "target_audience",
        "practical_info",
        "date_insert",
        "date_update",
        "source",
        "portal",
        "review",
        "published",
        "publication_date",
        "cities",
        "districts",
        "areas",
        "approved",
        "uuid",
        "provider",
        "bookable",
        "cancelled",
        "cancellation_reason"
        "place",
        'preparation_duration',
        'intervention_duration'
    ]
    COLUMNS_LISTS["feedback_export"] = [
        "comment",
        "activity",
        "category",
        "problem_magnitude",
        "status",
        "related_trek",
        "uuid",
        "eid",
        "external_eid",
        "locked",
        "origin"
        "date_update",
        "date_insert",
        "created_in_suricate",
        "last_updated_in_suricate",
        "assigned_user",
        "uses_timers"
    ]
    COLUMNS_LISTS["sensitivity_export"] = [
        "species",
        "published",
        "description",
        "contact",
        "pretty_period",
        "pretty_practices",
    ]
    COLUMNS_LISTS["outdoor_site_export"] = [
        "structure",
        "name",
        "practice",
        "description",
        "description_teaser",
        "ambiance",
        "advice",
        "accessibility",
        "period",
        "labels",
        "themes",
        "portal",
        "source",
        "information_desks",
        "web_links",
        "eid",
        "orientation",
        "wind",
        "ratings",
        "managers",
        "type",
        "description",
        "description_teaser",
        "ambiance",
        "period",
        "orientation",
        "wind",
        "labels",
        "themes",
        "portal",
        "source",
        "managers",
        "min_elevation",
        "date_insert",
        "date_update",
        "uuid",
    ]
    COLUMNS_LISTS["outdoor_course_export"] = [
        "structure",
        "name",
        "parent_sites",
        "description",
        "advice",
        "equipment",
        "accessibility",
        "eid",
        "height",
        "ratings",
        "gear",
        "duration"
        "ratings_description",
        "type",
        "points_reference",
        "uuid",
    ]

**Hideable form fields**

An exhaustive list of form fields hideable in each module.

::

    HIDDEN_FORM_FIELDS["path"] = [
            "departure",
            "name",
            "stake",
            "comfort",
            "arrival",
            "comments",
            "source",
            "networks",
            "usages",
            "valid",
            "draft",
            "reverse_geom",
        ],
    HIDDEN_FORM_FIELDS["trek"] = [
            "structure",
            "name",
            "review",
            "published",
            "labels",
            "departure",
            "arrival",
            "duration",
            "difficulty",
            "gear",
            "route",
            "ambiance",
            "access",
            "description_teaser",
            "description",
            "points_reference",
            "accessibility_infrastructure",
            "advised_parking",
            "parking_location",
            "public_transport",
            "advice",
            "themes",
            "networks",
            "practice",
            "accessibilities",
            "accessibility_advice",
            "accessibility_covering",
            "accessibility_exposure",
            "accessibility_level",
            "accessibility_signage",
            "accessibility_slope",
            "accessibility_width",
            "web_links",
            "information_desks",
            "source",
            "portal",
            "children_trek",
            "eid",
            "eid2",
            "ratings",
            "ratings_description",
            "reservation_system",
            "reservation_id",
            "pois_excluded",
            "hidden_ordered_children",
        ],
    HIDDEN_FORM_FIELDS["trail"] = [
            "departure",
            "arrival",
            "comments",
            "category",
        ],
    HIDDEN_FORM_FIELDS["landedge"] = [
            "owner",
            "agreement"
        ],
    HIDDEN_FORM_FIELDS["infrastructure"] = [
            "condition",
            "access",
            "description",
            "accessibility",
            "published",
            "implantation_year",
            "usage_difficulty",
            "maintenance_difficulty"
        ],
    HIDDEN_FORM_FIELDS["signage"] = [
            "condition",
            "description",
            "published",
            "implantation_year",
            "code",
            "printed_elevation",
            "manager",
            "sealing",
            "access"
        ],
    HIDDEN_FORM_FIELDS["intervention"] = [
            "disorders",
            "description",
            "type",
            "subcontracting",
            "length",
            "width",
            "height",
            "stake",
            "project",
            "material_cost",
            "heliport_cost",
            "subcontract_cost",
        ],
    HIDDEN_FORM_FIELDS["project"] = [
            "type",
            "type",
            "domain",
            "end_year",
            "constraint",
            "global_cost",
            "comments",
            "project_owner",
            "project_manager",
            "contractors",
        ],
    HIDDEN_FORM_FIELDS["site"] = [
            "parent",
            "review",
            "published",
            "practice",
            "description_teaser",
            "description",
            "ambiance",
            "advice",
            "period",
            "orientation",
            "wind",
            "labels",
            "themes",
            "information_desks",
            "web_links",
            "portal",
            "source",
            "managers",
            "eid"
        ],
    HIDDEN_FORM_FIELDS["course"] = [
            "review",
            "published",
            "description",
            "advice",
            "equipment",
            "accessibility",
            "height",
            "children_course",
            "eid",
            "gear",
            "duration"
            "ratings_description",
        ]
    HIDDEN_FORM_FIELDS["poi"] = [
            "review",
            "published",
            "description",
            "eid",
        ],
    HIDDEN_FORM_FIELDS["service"] = [
            "eid",
        ],
    HIDDEN_FORM_FIELDS["dive"] = [
            "review",
            "published",
            "practice",
            "advice",
            "description_teaser",
            "description",
            "difficulty",
            "levels",
            "themes",
            "owner",
            "depth",
            "facilities",
            "departure",
            "disabled_sport",
            "source",
            "portal",
            "eid",
        ],
    HIDDEN_FORM_FIELDS["touristic_content"] = [
            'label_accessibility'
            'type1',
            'type2',
            'review',
            'published',
            'accessibility',
            'description_teaser',
            'description',
            'themes',
            'contact',
            'email',
            'website',
            'practical_info',
            'approved',
            'source',
            'portal',
            'eid',
            'reservation_system',
            'reservation_id'
        ],
    HIDDEN_FORM_FIELDS["touristic_event"] = [
            'review',
            'published',
            'description_teaser',
            'description',
            'themes',
            'end_date',
            'duration',
            'meeting_point',
            'start_time',
            'end_time',
            'contact',
            'email',
            'website',
            'organizer',
            'speaker',
            'type',
            'accessibility',
            'capacity',
            'booking',
            'target_audience',
            'practical_info',
            'approved',
            'source',
            'portal',
            'eid',
            "bookable",
            'cancelled',
            'cancellation_reason'
            'place',
            'preparation_duration',
            'intervention_duration'
        ],
    HIDDEN_FORM_FIELDS["report"] = [
            "email",
            "comment",
            "activity",
            "category",
            "problem_magnitude",
            "related_trek",
            "status",
            "locked",
            "uid",
            "origin",
            "assigned_user",
            "uses_timers"
        ],
    HIDDEN_FORM_FIELDS["sensitivity_species"] = [
            "contact",
            "published",
            "description",
        ],
    HIDDEN_FORM_FIELDS["sensitivity_regulatory"] = [
            "contact",
            "published",
            "description",
            "pictogram",
            "elevation",
            "url",
            "period01",
            "period02",
            "period03",
            "period04",
            "period05",
            "period06",
            "period07",
            "period08",
            "period09",
            "period10",
            "period11",
            "period12",
        ],
    HIDDEN_FORM_FIELDS["blade"] = [
            "condition",
            "color",
        ],
    HIDDEN_FORM_FIELDS["report"] = [
            "comment",
            "activity",
            "category",
            "problem_magnitude",
            "related_trek",
            "status",
            "locked",
            "uid",
            "origin"
        ]


**Other settings**
::

    SEND_REPORT_ACK = True

If false, no mail will be sent to the sender of any feedback on Geotrek-rando website

::

    USE_BOOKLET_PDF = True

Use booklet for PDF. During the synchro, pois details will be removed, and the pages will be merged.
It is possible to customize the pdf, with trek_public_booklet_pdf.html.

::

    ALLOW_PATH_DELETION_TOPOLOGY = True

If false, it forbid to delete a path when at least one topology is linked to this path.


::

    ALERT_DRAFT = False

If True, it sends a message to managers (MANAGERS) whenever a path has been changed to draft.

Email configuration takes place in ``/opt/geotrek-admin/var/conf/custom.py``, where you control
recipients emails (``ADMINS``, ``MANAGERS``) and email server configuration.


::

    ALERT_REVIEW = False


If True, it sends a message to managers (MANAGERS) whenever an object which can be published has been changed to review mode.

Email configuration takes place in ``/opt/geotrek-admin/var/conf/custom.py``, where you control
recipients emails (``ADMINS``, ``MANAGERS``) and email server configuration.


**Custom SQL**
::
Put your custom SQL in a file name ``/opt/geotrek-admin/var/conf/extra_sql/<app name>/<pre or post>_<script name>.sql``

* app name is the name of the Django application, eg. trekking or tourism
* ``pre_``… scripts are executed before Django migrations and ``post_``… scripts after
* script are executed in INSTALLED_APPS order, then by alphabetical order of script names


**Manage Cache**
::
* You can purge application cache with command or in admin interface

::
    sudo geotrek clearcache --cache_name default --cache_name fat --cache_name api_v2h ori
