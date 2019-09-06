===============
Global Settings
===============
+-----------------------------------------+----------+--------------------------------------+-------------------------------------------------+--------------------------------------------------------+
| **Option**                              | **Type** | **Default**                          | **Description**                                 | **more information**                                   |
|                                         |          | *Necessary to change                 |                                                 |                                                        |
|                                         |          | before install*                      |                                                 |                                                        |
|                                         |          |                                      |                                                 |                                                        |
+-----------------------------------------+----------+--------------------------------------+-------------------------------------------------+--------------------------------------------------------+
|                                         |          |                                      |                                                 |                                                        |
+-----------------------------------------+----------+--------------------------------------+-------------------------------------------------+--------------------------------------------------------+
|                                         |          |                                      |                                                 |                                                        |
+-----------------------------------------+----------+--------------------------------------+-------------------------------------------------+--------------------------------------------------------+
|                                         |          |                                      |                                                 |                                                        |
+-----------------------------------------+----------+--------------------------------------+-------------------------------------------------+--------------------------------------------------------+
| SPATIAL_EXTENT                          | list     | **(105000, 6150000,                  | boundingbox : corner bottom left xy,            | Should not be change after install.                    |
|                                         |          | 1100000, 7150000)**                  | corner top right xy                             |                                                        |
|                                         |          |                                      | of your project                                 |                                                        |
+-----------------------------------------+----------+--------------------------------------+-------------------------------------------------+--------------------------------------------------------+
| TREKKING_TOPOLOGY_ENABLED               | boolean  | True                                 | Use dynamic segmentation or not.                | Do not change it after install, or dump your database  |
|                                         |          |                                      |                                                 | before.                                                |
+-----------------------------------------+----------+--------------------------------------+-------------------------------------------------+--------------------------------------------------------+
| FLATPAGES_ENABLED                       | boolean  | True                                 | Show flatpages on menus or not.                 | Can be change whenever you want.                       |
+-----------------------------------------+----------+--------------------------------------+-------------------------------------------------+--------------------------------------------------------+
| TOURISM_ENABLED                         | boolean  | True                                 | Show Tourism models (Touristic Event and        | Can be change whenever you want.                       |
|                                         |          |                                      | Touristic Content on menus or not               |                                                        |
+-----------------------------------------+----------+--------------------------------------+-------------------------------------------------+--------------------------------------------------------+
| PATH_SNAPPING_DISTANCE                  | float    | 1                                    | Distance of path snapping in metters            | Change the distance. Better to keep it like this.      |
|                                         |          |                                      |                                                 | Not used when TREKKING_TOPOLOGY_ENABLED = True         |
+-----------------------------------------+----------+--------------------------------------+-------------------------------------------------+--------------------------------------------------------+
| SNAP_DISTANCE                           | integer  | 30                                   | Distance of snapping for the cursor in pixels   | Change the distance.                                   |
|                                         |          |                                      | on map leaflet                                  |                                                        |
+-----------------------------------------+----------+--------------------------------------+-------------------------------------------------+--------------------------------------------------------+
| PATH_MERGE_SNAPPING_DISTANCE            | float    | 2                                    | Minimum distance to merge 2 paths               | Change the distance. Should be higher or the same as   |
|                                         |          |                                      |                                                 | PATH_SNAPPING_DISTANCE.                                |
|                                         |          |                                      |                                                 | Not used when TREKKING_TOPOLOGY_ENABLED = True         |
+-----------------------------------------+----------+--------------------------------------+-------------------------------------------------+--------------------------------------------------------+
| MAP_STYLES                              | dict     | Click to see                         | Color of the different layers on the map        | MAP_STYLES['path'] = {'weigth': 2, 'opacity': 2.0,     |
|                                         |          |                                      |                                                 | 'color': 'yellow'}                                     |
|                                         |          |                                      |                                                 | MAP_STYLES['city']['opacity'] = 0.8                    |
|                                         |          |                                      |                                                 |                                                        |
|                                         |          |                                      |                                                 |                                                        |
|                                         |          |                                      |                                                 | For color : color picker                               |
+-----------------------------------------+----------+--------------------------------------+-------------------------------------------------+--------------------------------------------------------+
| COLORS_POOL                             | dict     |                                      | Color of the different layers on the top right. | MAP_STYLES['restrictedarea'] = ['plum', 'violet',      |
|                                         |          |                                      |                                                 | 'deeppink']                                            |
|                                         |          |                                      |                                                 |                                                        |
|                                         |          |                                      |                                                 |                                                        |
|                                         |          |                                      |                                                 | For land, physical, competence, signagemanagement,     |
|                                         |          |                                      |                                                 | workmanagement should have 5 values.                   |
|                                         |          |                                      |                                                 |                                                        |
|                                         |          |                                      |                                                 | For restricted Area : add as many color as your        |
|                                         |          |                                      |                                                 | number of restricted area type                         |
+-----------------------------------------+----------+--------------------------------------+-------------------------------------------------+--------------------------------------------------------+
| TOURISM_INTERSECTION_MARGIN             | integer  | 500                                  | Distance to which tourist contents and          | This distance can be changed by practice in the admin. |
|                                         |          |                                      | tourist events will be displayed                |                                                        |
+-----------------------------------------+----------+--------------------------------------+-------------------------------------------------+--------------------------------------------------------+
| DIVING_INTERSECTION_MARGIN              | integer  | 500                                  | Distance to which dives will be displayed       |                                                        |
+-----------------------------------------+----------+--------------------------------------+-------------------------------------------------+--------------------------------------------------------+
| TREK_POINTS_OF_REFERENCE_ENABLED        | integer  | True                                 | Points of reference are enabled on form of      |                                                        |
|                                         |          |                                      | treks                                           |                                                        |
+-----------------------------------------+----------+--------------------------------------+-------------------------------------------------+--------------------------------------------------------+
| TREK_EXPORT_POI_LIST_LIMIT              | integer  | 14                                   | Limit of the number of pois on treks pdf        | 14 is already a huge amount of POI, but it's possible  |
|                                         |          |                                      |                                                 | to add more.                                           |
+-----------------------------------------+----------+--------------------------------------+-------------------------------------------------+--------------------------------------------------------+
| TREK_EXPORT_INFORMATION_DESK_LIST_LIMIT | integer  | 2                                    | Limit of the number of information desks on     | You can put -1 if you want all the information desks   |
|                                         |          |                                      | treks pdf                                       |                                                        |
+-----------------------------------------+----------+--------------------------------------+-------------------------------------------------+--------------------------------------------------------+
| SHOW_SENSITIVE_AREAS_ON_MAP_SCREENSHOT  | boolean  | True                                 | Show sensitive areas on maps of pdf             | Show sensitive areas only if app sensitivy is enabled  |
+-----------------------------------------+----------+--------------------------------------+-------------------------------------------------+--------------------------------------------------------+
| SHOW_POIS_ON_MAP_SCREENSHOT             | boolean  | True                                 | Show pois on maps of pdf                        |                                                        |
+-----------------------------------------+----------+--------------------------------------+-------------------------------------------------+--------------------------------------------------------+
| SHOW_SERVICES_ON_MAP_SCREENSHOT         | boolean  | True                                 | Show services on maps of pdf                    |                                                        |
+-----------------------------------------+----------+--------------------------------------+-------------------------------------------------+--------------------------------------------------------+
| SHOW_SIGNAGES_ON_MAP_SCREENSHOT         | boolean  | True                                 | Show signages on maps of pdf                    |                                                        |
+-----------------------------------------+----------+--------------------------------------+-------------------------------------------------+--------------------------------------------------------+
| SHOW_INFRASTRUCTURES_ON_MAP_SCREENSHOT  | boolean  | True                                 | Show infrastructures on maps of pdf             |                                                        |
+-----------------------------------------+----------+--------------------------------------+-------------------------------------------------+--------------------------------------------------------+
| TOPOLOGY_STATIC_OFFSETS                 | dict     | {'land': -5,                         | Land objects are added on other objects         | You should not change this settings, except if you     |
|                                         |          |  'physical': 0,                      | with offset.                                    | want to use less type. Example :                       |
|                                         |          |  'competence': 5,                    |                                                 |                                                        |
|                                         |          |  'signagemanagement': -10,           |                                                 | {'land': -5,                                           |
|                                         |          |  'workmanagement': 10}               |                                                 |  'competence': 0,                                      |
|                                         |          |                                      |                                                 |  'workmanagement': 5}                                  |
+-----------------------------------------+----------+--------------------------------------+-------------------------------------------------+--------------------------------------------------------+
| TREK_CATEGORY_ORDER                     | integer  | 1                                    | Order of all the treks without practice on      | All the settings about order are the order inside      |
|                                         |          |                                      | 'Rando' web site                                | rando web site.                                        |
|                                         |          |                                      |                                                 | Practices of diving, treks and touristic contents are  |
|                                         |          |                                      |                                                 | taken in account Treks without practices will          |
|                                         |          |                                      |                                                 | be first.                                              |
+-----------------------------------------+----------+--------------------------------------+-------------------------------------------------+--------------------------------------------------------+
| ITINERANCY_CATEGORY_ORDER               | integer  | 2                                    | Order of itinerancy on 'Rando' web site         | Itinerancy will be second only if there are itinerancy |
+-----------------------------------------+----------+--------------------------------------+-------------------------------------------------+--------------------------------------------------------+
| DIVE_CATEGORY_ORDER                     | integer  | 10                                   | Order of dives on 'Rando' web site              | Dives will be third if there are no treks              |
|                                         |          |                                      |                                                 | with practices                                         |
+-----------------------------------------+----------+--------------------------------------+-------------------------------------------------+--------------------------------------------------------+
| TOURISTIC_EVENT_CATEGORY_ORDER          | integer  | 99                                   | Order of touristic events on 'Rando' web site   | Touristic events will be last.                         |
+-----------------------------------------+----------+--------------------------------------+-------------------------------------------------+--------------------------------------------------------+
| SPLIT_TREKS_CATEGORIES_BY_PRACTICE      | boolean  | False                                | On the Rando web site, treks                    | Order in admin will be take in account                 |
|                                         |          |                                      | practices will be displayed separately          |                                                        |
+-----------------------------------------+----------+--------------------------------------+-------------------------------------------------+--------------------------------------------------------+
| SPLIT_TREKS_CATEGORIES_BY_ACCESSIBILITY | boolean  | False                                | On the Rando web site,                          |                                                        |
|                                         |          |                                      | accessibilites will be displayed separately     |                                                        |
+-----------------------------------------+----------+--------------------------------------+-------------------------------------------------+--------------------------------------------------------+
| SPLIT_TREKS_CATEGORIES_BY_ITINERANCY    | boolean  | False                                | On the Rando web site,                          |                                                        |
|                                         |          |                                      | if a trek has a children it will be displayed   |                                                        |
|                                         |          |                                      |  separately                                     |                                                        |
+-----------------------------------------+----------+--------------------------------------+-------------------------------------------------+--------------------------------------------------------+
| SPLIT_DIVES_CATEGORIES_BY_PRACTICE      | boolean  | True                                 | On the Rando web site, dives                    |                                                        |
|                                         |          |                                      | practices will be displayed separately          |                                                        |
+-----------------------------------------+----------+--------------------------------------+-------------------------------------------------+--------------------------------------------------------+
| HIDE_PUBLISHED_TREKS_IN_TOPOLOGIES      | boolean  | False                                | On the 'Rando' web site, treks near other       |                                                        |
|                                         |          |                                      | are hide                                        |                                                        |
+-----------------------------------------+----------+--------------------------------------+-------------------------------------------------+--------------------------------------------------------+
| MOBILE_TILES_URL                        | list     | ['https://{s}.tile.                  |                                                 |                                                        |
|                                         |          | 'opentopomap.org'                    |                                                 |                                                        |
|                                         |          | '/{z}/{x}/{y}.png']                  |                                                 |                                                        |
+-----------------------------------------+----------+--------------------------------------+-------------------------------------------------+--------------------------------------------------------+
| MOBILE_LENGTH_INTERVALS                 | list     | [{"id": 1,                           | Intervals of the mobile for the length filter   |                                                        |
|                                         |          |   "name": "< 10 km",                 |                                                 |                                                        |
|                                         |          |   "interval": [0, 9999]},            |                                                 |                                                        |
|                                         |          |  {"id": 2,                           |                                                 |                                                        |
|                                         |          |   "name": "10 - 30",                 |                                                 |                                                        |
|                                         |          |   "interval": [9999, 29999]},        |                                                 |                                                        |
|                                         |          |  {"id": 3,                           |                                                 |                                                        |
|                                         |          |   "name": "30 - 50",                 |                                                 |                                                        |
|                                         |          |   "interval": [30000, 50000]},       |                                                 |                                                        |
|                                         |          |  {"id": 4,                           |                                                 |                                                        |
|                                         |          |   "name": "> 50 km",                 |                                                 |                                                        |
|                                         |          |   "interval": [50000, 999999]}]      |                                                 |                                                        |
+-----------------------------------------+----------+--------------------------------------+-------------------------------------------------+--------------------------------------------------------+
| MOBILE_ASCENT_INTERVALS                 | list     | [{"id": 1,                           | Intervals of the mobile for the ascent filter   |                                                        |
|                                         |          |   "name": "< 300 m",                 |                                                 |                                                        |
|                                         |          |   "interval": [0, 299]},             |                                                 |                                                        |
|                                         |          |  {"id": 2,                           |                                                 |                                                        |
|                                         |          |   "name": "300 - 600",               |                                                 |                                                        |
|                                         |          |   "interval": [300, 599]},           |                                                 |                                                        |
|                                         |          |  {"id": 3,                           |                                                 |                                                        |
|                                         |          |   "name": "600 - 1000",              |                                                 |                                                        |
|                                         |          |   "interval": [600, 999]},           |                                                 |                                                        |
|                                         |          |  {"id": 4,                           |                                                 |                                                        |
|                                         |          |   "name": "> 1000 m",                |                                                 |                                                        |
|                                         |          |   "interval": [1000, 9999]}]         |                                                 |                                                        |
+-----------------------------------------+----------+--------------------------------------+-------------------------------------------------+--------------------------------------------------------+
| MOBILE_DURATION_INTERVALS               | list     | [{"id": 1,                           | Intervals of the mobile for the duration filter |                                                        |
|                                         |          |   "name": "< 1 heure",               |                                                 |                                                        |
|                                         |          |   "interval": [0, 1]},               |                                                 |                                                        |
|                                         |          |  {"id": 2,                           |                                                 |                                                        |
|                                         |          |   "name": "1h - 2h30",               |                                                 |                                                        |
|                                         |          |   "interval": [1, 2.5]},             |                                                 |                                                        |
|                                         |          |  {"id": 3,                           |                                                 |                                                        |
|                                         |          |   "name": "2h30 - 5h",               |                                                 |                                                        |
|                                         |          |   "interval": [2.5, 5]},             |                                                 |                                                        |
|                                         |          |  {"id": 4,                           |                                                 |                                                        |
|                                         |          |   "name": "5h - 9h",                 |                                                 |                                                        |
|                                         |          |   "interval": [5, 9]},               |                                                 |                                                        |
|                                         |          |  {"id": 5,                           |                                                 |                                                        |
|                                         |          |   "name": "> 9h",                    |                                                 |                                                        |
|                                         |          |   "interval": [9, 9999999]}]         |                                                 |                                                        |
+-----------------------------------------+----------+--------------------------------------+-------------------------------------------------+--------------------------------------------------------+
| SYNC_RANDO_ROOT                         | string   | os.path.join(VAR_DIR, 'data')        | Path on your server wehre the datas for rando   | If you want to change it, you should import os         |
|                                         |          | */<instance_Geotrek>/<var_dir>/data* | web site will be generated                      | at the top of your file and do something similar to    |
|                                         |          |                                      |                                                 | the default                                            |
+-----------------------------------------+----------+--------------------------------------+-------------------------------------------------+--------------------------------------------------------+
| SYNC_MOBILE_ROOT                        | string   | os.path.join(VAR_DIR, 'mobile')      | Path on your server wehre the datas for mobile  | If you want to change it, you should import os         |
|                                         |          | /<instance_Geotrek>/<var_dir>/mobile | will be generated                               | at the top of your file and do something similar to    |
|                                         |          |                                      |                                                 | the default                                            |
+-----------------------------------------+----------+--------------------------------------+-------------------------------------------------+--------------------------------------------------------+
| SYNC_RANDO_OPTIONS                      | dict     | {}                                   | Options of the sync_rando command               |                                                        |
+-----------------------------------------+----------+--------------------------------------+-------------------------------------------------+--------------------------------------------------------+
| SYNC_MOBILE_OPTIONS                     | dict     | {'skip_tiles': False}                | Options of the sync_mobile command              |                                                        |
+-----------------------------------------+----------+--------------------------------------+-------------------------------------------------+--------------------------------------------------------+
| TREK_WITH_POIS_PICTURES                 | boolean  | False                                |                                                 |                                                        |
|                                         |          |                                      | Geotrek Rando it enables correlated pictures    |                                                        |
|                                         |          |                                      | to be displayed in the slideshow.               |                                                        |
+-----------------------------------------+----------+--------------------------------------+-------------------------------------------------+--------------------------------------------------------+
| BLADE_CODE_TYPE                         | type     | int                                  | Type of the blade code                          | It can be str or int.                                  |
|                                         |          |                                      |                                                 | If you have an integer code : int                      |
|                                         |          |                                      |                                                 | If you have an string code : str                       |
+-----------------------------------------+----------+--------------------------------------+-------------------------------------------------+--------------------------------------------------------+
| BLADE_CODE_FORMAT                       | str      | "{signagecode}-{bladenumber}"        | Correspond of the format showed on export of    | If you want to change : move information under bracket |
|                                         |          |                                      | blades code                                     | You can also remove one element between bracket        |
|                                         |          |                                      |                                                 | You can do for exemple :                               |
|                                         |          |                                      |                                                 | "CD99.{signagecode}.{bladenumber}"                     |
|                                         |          |                                      |                                                 | It will display : CD99.XIDNZEIU.01                     |
|                                         |          |                                      |                                                 | signagecode is the code of the signage                 |
|                                         |          |                                      |                                                 | bladenumber is the number of the blade                 |
+-----------------------------------------+----------+--------------------------------------+-------------------------------------------------+--------------------------------------------------------+
| LINE_CODE_FORMAT                        | str      | "{signagecode}-{bladenumber}"        | Correspond of the format showed on export       | Similar with above                                     |
|                                         |          | "-{linenumber}"                      | of lines code                                   | You can do for example :                               |
|                                         |          |                                      |                                                 | "CD99.{signagecode}-{bladenumber}.{linenumber}"        |
|                                         |          |                                      |                                                 | It will display : CD99.XIDNZEIU-01.01                  |
|                                         |          |                                      |                                                 | signagecode is the code of the signage                 |
|                                         |          |                                      |                                                 | bladenumber is the number of the blade                 |
|                                         |          |                                      |                                                 | linenumber is the number of the line                   |
+-----------------------------------------+----------+--------------------------------------+-------------------------------------------------+--------------------------------------------------------+
| THUMBNAIL_COPYRIGHT_FORMAT              | str      | ""                                   | Add a thumbnail on every picture for rando      | Example :                                              |
|                                         |          |                                      | web site.                                       | "{title} {author} {legend}"                            |
|                                         |          |                                      |                                                 | Will display title of the picture the author           |
|                                         |          |                                      |                                                 | on Geotrek and the legend                              |
+-----------------------------------------+----------+--------------------------------------+-------------------------------------------------+--------------------------------------------------------+
| THUMBNAIL_COPYRIGHT_SIZE                | int      | 15                                   | Size of you thumbnail                           |                                                        |
+-----------------------------------------+----------+--------------------------------------+-------------------------------------------------+--------------------------------------------------------+
| ENABLED_MOBILE_FILTERS                  | list     | ['practice', 'difficulty',           | List of all the filters enabled on mobile.      | Remove any of the filters,                             |
|                                         |          |  'durations', 'ascent',              |                                                 | if you don't want one of them.                         |
|                                         |          |  'lengths', 'themes',                |                                                 |                                                        |
|                                         |          |  'route', 'districts',               |                                                 | It's useless to add other one.                         |
|                                         |          |  'cities', 'accessibilities',]       |                                                 |                                                        |
+-----------------------------------------+----------+--------------------------------------+-------------------------------------------------+--------------------------------------------------------+
| PRIMARY_COLOR                           | str      | "#7b8c12"                            | Primary color of your pdf                       | Check : "color picker"                                 |
+-----------------------------------------+----------+--------------------------------------+-------------------------------------------------+--------------------------------------------------------+
| ONLY_EXTERNAL_PUBLIC_PDF                | boolean  | False                                | If True, on rando web site, only pdf imported   |                                                        |
|                                         |          |                                      | with FileType : "Topoguide"                     |                                                        |
|                                         |          |                                      | and not autogenerated                           |                                                        |
+-----------------------------------------+----------+--------------------------------------+-------------------------------------------------+--------------------------------------------------------+
| SEND_REPORT_ACK                         | boolean  | True                                 | If false, no mail will be sent to the sender of |                                                        |
|                                         |          |                                      | any feedback on Rando web site                  |                                                        |
+-----------------------------------------+----------+--------------------------------------+-------------------------------------------------+--------------------------------------------------------+