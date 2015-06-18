{% set cfg = salt['mc_project.get_configuration'](project) %}
{% set data = cfg.data %}
from .prod import *


# Necessary block of config when maps are not from Geotrek Tilecache :
LEAFLET_CONFIG['SRID'] = 3857
LEAFLET_CONFIG['TILES'] = [
    (gettext_noop('Scan'), 'http://gpp3-wxs.ign.fr/158os34s66xqcvdwzyivp1m0/geoportail/wmts?LAYER=GEOGRAPHICALGRIDSYSTEMS.MAPS.SCAN-EXPRESS.CLASSIQUE&EXCEPTIONS=image/jpeg&FORMAT=image/jpeg&SERVICE=WMTS&VERSION=1.0.0&REQUEST=GetTile&STYLE=normal&TILEMATRIXSET=PM&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}',
     '&copy; IGN - GeoPortail'),
    (gettext_noop('Ortho'), 'http://{s}.tiles.cg44.makina-corpus.net/ortho-2012/{z}/{x}/{y}.jpg', {'attribution': 'Source: Département de Loire-Atlantique', 'tms': True}),
]

MOBILE_TILES_URL = LEAFLET_CONFIG['TILES'][0][1]

TREKKING_TOPOLOGY_ENABLED = False
TRAIL_MODEL_ENABLED = False

INSTALLED_APPS = list(INSTALLED_APPS)
INSTALLED_APPS.remove('geotrek.land')
INSTALLED_APPS.remove('geotrek.maintenance')
INSTALLED_APPS.remove('geotrek.infrastructure')

SPLIT_TREKS_CATEGORIES_BY_PRACTICE = True
SPLIT_TREKS_CATEGORIES_BY_ACCESSIBILITY = True
