{% set cfg = salt['mc_project.get_configuration'](project) %}
{% set data = cfg.data %}
from .prod import *
ALTIMETRIC_PROFILE_COLOR = '#33b652'

LEAFLET_CONFIG['TILES'] = [
    (gettext_noop('Scan'), 'http://{s}.tile.osm.org/{z}/{x}/{y}.png', '(c) OpenStreetMap Contributors'),
    (gettext_noop('Ortho'), 'http://{s}.tiles.mapbox.com/v3/openstreetmap.map-4wvf9l0l/{z}/{x}/{y}.jpg', '(c) MapBox'),
]


LEAFLET_CONFIG['SRID'] = 3857

TREKKING_TOPOLOGY_ENABLED = False
TRAIL_MODEL_ENABLED = False

_INSTALLED_APPS = list(INSTALLED_APPS)
_INSTALLED_APPS.remove('geotrek.land')
_INSTALLED_APPS.remove('geotrek.maintenance')
_INSTALLED_APPS.remove('geotrek.infrastructure')

INSTALLED_APPS = _INSTALLED_APPS

