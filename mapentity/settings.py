from collections import OrderedDict

from django.conf import settings


API_SRID = 4326

app_settings = dict({
    'TITLE': "",
    'HISTORY_ITEMS_MAX': 5,
    'CONVERSION_SERVER': 'http://convertit/',
    'CAPTURE_SERVER': 'http://screamshotter/',
    'INTERNAL_USER': '__internal__',
    'JS_SETTINGS_VIEW': 'mapentity:js_settings',
    'ROOT_URL': '',
    'LANGUAGES': settings.LANGUAGES,
    'TRANSLATED_LANGUAGES': settings.LANGUAGES,
    'LANGUAGE_CODE': settings.LANGUAGE_CODE,
    'TEMP_DIR': getattr(settings, 'TEMP_DIR', None),
    'MAP_CAPTURE_SIZE': 800,
    'MAP_CAPTURE_MAX_RATIO': 1.25,
    'GEOM_FIELD_NAME': 'geom',
    'DATE_UPDATE_FIELD_NAME': 'date_update',
    'MAP_BACKGROUND_FOGGED': False,
    'MAP_FIT_MAX_ZOOM': 18,
    'ACTION_HISTORY_ENABLED': True,
    'ACTION_HISTORY_LENGTH': 20,
    'ANONYMOUS_VIEWS_PERMS': tuple(),
    'GEOJSON_LAYERS_CACHE_BACKEND': 'default',
    'GEOJSON_PRECISION': None,
    'SERVE_MEDIA_AS_ATTACHMENT': True,
    'SENDFILE_HTTP_HEADER': None,
    'DRF_API_URL_PREFIX': r'^api/',
    'MAPENTITY_WEASYPRINT': False,
}, **getattr(settings, 'MAPENTITY_CONFIG', {}))


TINYMCE_DEFAULT_CONFIG = {
    'theme': 'advanced',
    'theme_advanced_buttons1': 'bold,italic,forecolor,separator,bullist,numlist,link,media,separator,undo,redo,\
separator,cleanup,code',
    'theme_advanced_buttons2': '',
    'theme_advanced_buttons3': '',
    'theme_advanced_statusbar_location': 'bottom',
    'theme_advanced_toolbar_location': 'top',
    'theme_advanced_toolbar_align': 'center',
    'theme_advanced_resizing': True,
    'theme_advanced_resize_horizontal': False,
    'forced_root_block': False,
    'plugins': 'media,paste',
    'paste_auto_cleanup_on_paste': True,
    'width': '95%',
    'resize': "both",
    'valid_elements': ('@[id|class|style|title|dir<ltr?rtl|lang|xml::lang],'
                       'a[rel|rev|charset|hreflang|tabindex|accesskey|type|name|href|target|title|class],'
                       'img[longdesc|usemap|src|border|alt=|title|hspace|vspace|width|height|align],'
                       'p,em/i,strong/b,div[align],br,ul,li,ol,span[style],'
                       'iframe[src|frameborder=0|alt|title|width|height|align|name]'),
}
TINYMCE_DEFAULT_CONFIG.update(getattr(settings, 'TINYMCE_DEFAULT_CONFIG', {}))
setattr(settings, 'TINYMCE_DEFAULT_CONFIG', TINYMCE_DEFAULT_CONFIG)


REST_FRAMEWORK_DEFAULT_CONFIG = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'mapentity.models.MapEntityRestPermissions'
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'mapentity.renderers.GeoJSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
}
REST_FRAMEWORK_DEFAULT_CONFIG.update(getattr(settings, 'REST_FRAMEWORK', {}))
setattr(settings, 'REST_FRAMEWORK', REST_FRAMEWORK_DEFAULT_CONFIG)


_MAP_STYLES = {
    'detail': {'weight': 5, 'opacity': 1, 'color': 'yellow', 'arrowColor': '#FF5E00', 'arrowSize': 8},
    'others': {'opacity': 0.9, 'fillOpacity': 0.7, 'color': 'yellow'},
    'filelayer': {'color': 'red', 'opacity': 1.0, 'fillOpacity': 0.9, 'weight': 2, 'radius': 5},
    'draw': {'color': '#35FF00', 'opacity': 0.8, 'weight': 3},
    'print': {},
}


_LEAFLET_PLUGINS = OrderedDict([
    ('leaflet.overintent', {
        'js': 'mapentity/Leaflet.OverIntent/leaflet.overintent.js',
    }),
    ('leaflet.label', {
        'css': 'mapentity/Leaflet.label/dist/leaflet.label.css',
        'js': 'mapentity/Leaflet.label/dist/leaflet.label.js'
    }),
    ('leaflet.spin', {
        'js': ['paperclip/spin.min.js',
               'mapentity/Leaflet.Spin/leaflet.spin.js']
    }),
    ('leaflet.layerindex', {
        'js': ['mapentity/RTree/src/rtree.js',
               'mapentity/Leaflet.LayerIndex/leaflet.layerindex.js']
    }),
    ('leaflet.filelayer', {
        'js': ['mapentity/togeojson/togeojson.js',
               'mapentity/Leaflet.FileLayer/leaflet.filelayer.js']
    }),
    ('leaflet.geometryutil', {
        'js': 'mapentity/Leaflet.GeometryUtil/dist/leaflet.geometryutil.js'
    }),
    ('forms', {}),
    ('leaflet.snap', {
        'js': 'mapentity/Leaflet.Snap/leaflet.snap.js'
    }),
    ('leaflet.measurecontrol', {
        'css': 'mapentity/Leaflet.MeasureControl/leaflet.measurecontrol.css',
        'js': 'mapentity/Leaflet.MeasureControl/leaflet.measurecontrol.js'
    }),
    ('leaflet.fullscreen', {
        'css': 'mapentity/leaflet.fullscreen/Control.FullScreen.css',
        'js': 'mapentity/leaflet.fullscreen/Control.FullScreen.js'
    }),
    ('leaflet.groupedlayercontrol', {
        'css': 'mapentity/Leaflet.groupedlayercontrol/src/leaflet.groupedlayercontrol.css',
        'js': 'mapentity/Leaflet.groupedlayercontrol/src/leaflet.groupedlayercontrol.js'
    }),
    ('mapentity', {
        'js': ['mapentity/mapentity.js',
               'mapentity/mapentity.forms.js'],
    })
])

_LEAFLET_CONFIG = getattr(settings, 'LEAFLET_CONFIG', {})
_LEAFLET_PLUGINS.update(_LEAFLET_CONFIG.get('PLUGINS', {}))  # mapentity plugins first
_LEAFLET_CONFIG['PLUGINS'] = _LEAFLET_PLUGINS
setattr(settings, 'LEAFLET_CONFIG', _LEAFLET_CONFIG)
