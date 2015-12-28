from .prod import *  # noqa


LEAFLET_CONFIG['TILES'] = [
    # (gettext_noop('Scan'), 'http://{s}.tilestream.makina-corpus.net/v2/osmtopo/{z}/{x}/{y}.png', '&copy; OSM contributors - Topo by Makina Corpus'),
    (gettext_noop('OSM'), 'http://{s}.tile.osm.org/{z}/{x}/{y}.png', '&copy; OSM contributors'),
    (gettext_noop('Ortho'), 'https://{s}.tiles.mapbox.com/v3/makina-corpus.i3p1001l/{z}/{x}/{y}.png', '&copy; MapBox Satellite'),
]
LEAFLET_CONFIG['SRID'] = 3857

ALTIMETRIC_PROFILE_COLOR = '#F77E00'

MAPENTITY_CONFIG['MAP_BACKGROUND_FOGGED'] = False
MAPENTITY_CONFIG['MAP_FIT_MAX_ZOOM'] = 17
SPLIT_TREKS_CATEGORIES_BY_PRACTICE = True
MAPENTITY_CONFIG['MAPENTITY_WEASYPRINT'] = True
SYNC_RANDO_ROOT = '/srv/projects/geotrek/project/data'
SYNC_RANDO_OPTIONS = {'with_events': True, 'content_categories': '1,2,3,4,5,6,7,8'}

EXPORT_MAP_IMAGE_SIZE = {
    'trek': (18.2, 18.2),
    'poi': (18.2, 18.2),
    'touristiccontent': (18.2, 18.2),
    'touristicevent': (18.2, 18.2),
}
