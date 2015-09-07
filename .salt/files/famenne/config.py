{% set cfg = salt['mc_project.get_configuration'](project) %}
{% set data = cfg.data %}
from .prod import *


# Necessary block of config when maps are not from Geotrek Tilecache :
LEAFLET_CONFIG['SRID'] = 3857
LEAFLET_CONFIG['TILES'] = [
    (gettext_noop('Scan'), 'http://www.ngi.be/cartoweb/1.0.0/topo/default/3857/{z}/{y}/{x}.png',
     'NGI &copy; IGN - topomapviewer'),
    (gettext_noop('Ortho'), 'http://www.ngi.be/topomapviewer/services/1.0.0/RD_ORTHO_COL_CACHE/default/3857f/latest/{z}/{y}/{x}.png',
     'NGI &copy; IGN - topomapviewer'),
]

SPLIT_TREKS_CATEGORIES_BY_PRACTICE = True
TOURISM_INTERSECTION_MARGIN = 5000  # 5 km
