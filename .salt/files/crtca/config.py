{% set cfg = salt['mc_project.get_configuration'](project) %}
{% set data = cfg.data %}
from .prod import *


# Necessary block of config when maps are not from Geotrek Tilecache :
LEAFLET_CONFIG['SRID'] = 3857
LEAFLET_CONFIG['TILES'] = [
    (gettext_noop('Scan'), 'http://gpp3-wxs.ign.fr/f9an5dduzx730f47doku6vdv/geoportail/wmts?LAYER=GEOGRAPHICALGRIDSYSTEMS.MAPS&EXCEPTIONS=image/jpeg&FORMAT=image/jpeg&SERVICE=WMTS&VERSION=1.0.0&REQUEST=GetTile&STYLE=normal&TILEMATRIXSET=PM&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}',
     '&copy; IGN - GeoPortail'),
    (gettext_noop('Ortho'), 'http://gpp3-wxs.ign.fr/f9an5dduzx730f47doku6vdv/geoportail/wmts?LAYER=ORTHOIMAGERY.ORTHOPHOTOS&EXCEPTIONS=image/jpeg&FORMAT=image/jpeg&SERVICE=WMTS&VERSION=1.0.0&REQUEST=GetTile&STYLE=normal&TILEMATRIXSET=PM&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}',
     '&copy; IGN - GeoPortail'),
]

SPLIT_TREKS_CATEGORIES_BY_PRACTICE = True
