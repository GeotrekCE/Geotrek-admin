# -*- coding: utf-8 -*-
from .prod import *  # NOQA


# Necessary block of config when maps are not from Geotrek Tilecache :
LEAFLET_CONFIG['SRID'] = 3857
LEAFLET_CONFIG['TILES'] = [
    # *** SCAN ***
    (gettext_noop('Scan Express Standard'), 'http://gpp3-wxs.ign.fr/158os34s66xqcvdwzyivp1m0/geoportail/wmts?LAYER=GEOGRAPHICALGRIDSYSTEMS.MAPS.SCAN-EXPRESS.STANDARD&EXCEPTIONS=image/jpeg&FORMAT=image/jpeg&SERVICE=WMTS&VERSION=1.0.0&REQUEST=GetTile&STYLE=normal&TILEMATRIXSET=PM&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}', '&copy; IGN - GeoPortail'),
    (gettext_noop('Scan Express Classique'), 'http://gpp3-wxs.ign.fr/158os34s66xqcvdwzyivp1m0/geoportail/wmts?LAYER=GEOGRAPHICALGRIDSYSTEMS.MAPS.SCAN-EXPRESS.CLASSIQUE&EXCEPTIONS=image/jpeg&FORMAT=image/jpeg&SERVICE=WMTS&VERSION=1.0.0&REQUEST=GetTile&STYLE=normal&TILEMATRIXSET=PM&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}', '&copy; IGN - GeoPortail'),
    # *** ORTHO ***
    (gettext_noop('Orthophoto'), 'http://gpp3-wxs.ign.fr/158os34s66xqcvdwzyivp1m0/geoportail/wmts?LAYER=ORTHOIMAGERY.ORTHOPHOTOS&EXCEPTIONS=image/jpeg&FORMAT=image/jpeg&SERVICE=WMTS&VERSION=1.0.0&REQUEST=GetTile&STYLE=normal&TILEMATRIXSET=PM&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}', '&copy; IGN - GeoPortail'),
    # *** Ortho vuduciel CG44 (problème avec les tuiles png transparentes pour le découpage) ***
    # (gettext_noop('Ortho'), 'http://{s}.tiles.cg44.makina-corpus.net/ortho-2012/{z}/{x}/{y}.jpg', {'attribution': 'Source: Département de Loire-Atlantique', 'tms': True}),
]

TREKKING_TOPOLOGY_ENABLED = False
TRAIL_MODEL_ENABLED = False

INSTALLED_APPS = list(INSTALLED_APPS)
INSTALLED_APPS.remove('geotrek.land')
INSTALLED_APPS.remove('geotrek.maintenance')
INSTALLED_APPS.remove('geotrek.infrastructure')

SPLIT_TREKS_CATEGORIES_BY_PRACTICE = True
HIDE_PUBLISHED_TREKS_IN_TOPOLOGIES = True
ZIP_TOURISTIC_CONTENTS_AS_POI = True

THUMBNAIL_ALIASES['']['print'] = {'size': (800, 600), 'crop': 'smart'}
EXPORT_HEADER_IMAGE_SIZE = {
    'trek': (10.7, 8.025),
    'poi': (10.7, 8.025),
    'touristiccontent': (10.7, 8.025),
    'touristicevent': (10.7, 8.025),
}
