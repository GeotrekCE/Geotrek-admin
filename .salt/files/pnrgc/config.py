{% set cfg = salt['mc_project.get_configuration'](project) %}
{% set data = cfg.data %}
from .prod import *


# Adjustments PDF exports
ALTIMETRIC_PROFILE_COLOR = '#33b652'
ALTIMETRIC_PROFILE_FONT = 'Archer-Book'

# Asked by J.Atche :
LEAFLET_CONFIG['MAX_ZOOM'] = 20
PATH_SNAPPING_DISTANCE = 3  # meters

# Necessary block of config when maps are not from Geotrek Tilecache :
LEAFLET_CONFIG['SRID'] = 3857
LEAFLET_CONFIG['TILES'] = [
    (gettext_noop('Scan'), 'http://gpp3-wxs.ign.fr/ilbpmecqb9rugpmbx4ojtt98/geoportail/wmts?LAYER=GEOGRAPHICALGRIDSYSTEMS.MAPS.SCAN-EXPRESS.CLASSIQUE&EXCEPTIONS=image/jpeg&FORMAT=image/jpeg&SERVICE=WMTS&VERSION=1.0.0&REQUEST=GetTile&STYLE=normal&TILEMATRIXSET=PM&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}',
     '&copy; IGN - GeoPortail'),
    (gettext_noop('Ortho'), 'http://gpp3-wxs.ign.fr/ilbpmecqb9rugpmbx4ojtt98/geoportail/wmts?LAYER=ORTHOIMAGERY.ORTHOPHOTOS&EXCEPTIONS=image/jpeg&FORMAT=image/jpeg&SERVICE=WMTS&VERSION=1.0.0&REQUEST=GetTile&STYLE=normal&TILEMATRIXSET=PM&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}',
     '&copy; IGN - GeoPortail'),
]

LEAFLET_CONFIG['OVERLAYS'] = [
    (gettext_noop('Cadastre'), 'http://gpp3-wxs.ign.fr/ilbpmecqb9rugpmbx4ojtt98/geoportail/wmts?LAYER=CADASTRALPARCELS.PARCELS&STYLE=bdparcellaire&EXCEPTIONS=image/jpeg&FORMAT=image/png&SERVICE=WMTS&VERSION=1.0.0&REQUEST=GetTile&STYLE=normal&TILEMATRIXSET=PM&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}',
     '&copy; IGN - GeoPortail'),
]

TINYMCE_DEFAULT_CONFIG = {
    'theme': 'advanced',
    'theme_advanced_buttons1': 'bold,italic,forecolor,separator,bullist,numlist,link,media,separator,undo,redo,separator,cleanup,code',
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
