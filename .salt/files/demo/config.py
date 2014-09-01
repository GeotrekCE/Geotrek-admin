from .prod import *


LEAFLET_CONFIG['TILES'] = [
    (gettext_noop('Scan'), 'http://{s}.livembtiles.makina-corpus.net/makina/OSMTopo/{z}/{x}/{y}.png', '&copy; OSM contributors - Topo by Makina Corpus'),
    (gettext_noop('OSM'), 'http://{s}.tile.osm.org/{z}/{x}/{y}.png', '&copy; OSM contributors'),
    (gettext_noop('Ortho'), 'https://{s}.tiles.mapbox.com/v3/makina-corpus.i3p1001l/{z}/{x}/{y}.png', '&copy; MapBox Satellite'),
]
LEAFLET_CONFIG['SRID'] = 3857

ALTIMETRIC_PROFILE_COLOR = '#F77E00'

MAPENTITY_CONFIG['MAP_BACKGROUND_FOGGED'] = False

