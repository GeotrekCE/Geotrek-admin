{% set cfg = salt['mc_project.get_configuration'](project) %}
{% set data = cfg.data %}
from .prod import *


# Necessary block of config when maps are not from Geotrek Tilecache :
LEAFLET_CONFIG['SRID'] = 3857
LEAFLET_CONFIG['TILES'] = [
    (gettext_noop('Scan'), 'http://gpp3-wxs.ign.fr/hqsgqtv0l9d8a2k2ene94fdq/geoportail/wmts?LAYER=GEOGRAPHICALGRIDSYSTEMS.MAPS.SCAN-EXPRESS.CLASSIQUE&EXCEPTIONS=image/jpeg&FORMAT=image/jpeg&SERVICE=WMTS&VERSION=1.0.0&REQUEST=GetTile&STYLE=normal&TILEMATRIXSET=PM&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}',
     '&copy; IGN - GeoPortail'),
    (gettext_noop('Ortho'), 'http://gpp3-wxs.ign.fr/hqsgqtv0l9d8a2k2ene94fdq/geoportail/wmts?LAYER=ORTHOIMAGERY.ORTHOPHOTOS&EXCEPTIONS=image/jpeg&FORMAT=image/jpeg&SERVICE=WMTS&VERSION=1.0.0&REQUEST=GetTile&STYLE=normal&TILEMATRIXSET=PM&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}',
     '&copy; IGN - GeoPortail'),
    (gettext_noop('Cadastre'), 'http://gpp3-wxs.ign.fr/hqsgqtv0l9d8a2k2ene94fdq/geoportail/wmts?LAYER=CADASTRALPARCELS.PARCELS&EXCEPTIONS=image/jpeg&FORMAT=image/png&SERVICE=WMTS&VERSION=1.0.0&REQUEST=GetTile&STYLE=normal&TILEMATRIXSET=PM&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}',
     '&copy; IGN - GeoPortail'),
]

TREKKING_TOPOLOGY_ENABLED = False
TRAIL_MODEL_ENABLED = False
_INSTALLED_APPS = list(INSTALLED_APPS)
_INSTALLED_APPS.remove('geotrek.land')
_INSTALLED_APPS.remove('geotrek.maintenance')
_INSTALLED_APPS.remove('geotrek.infrastructure')
INSTALLED_APPS = _INSTALLED_APPS
