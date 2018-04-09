"""

Extends geotrek.settings.base using values coming
from a .INI file (default: etc/settings.ini).

It prevents users from editing a python file to configure Geotrek,
and provides a way to restrict the set of configurable options.

In addition, the same .INI file is used by buildout in order to
create config files of nginx, etc.

"""

from django.conf.global_settings import LANGUAGES as LANGUAGES_LIST
from django.contrib.gis.geos import fromstr

from .base import *


DEPLOY_ROOT = os.getenv('DEPLOY_ROOT', os.path.dirname(PROJECT_ROOT_PATH))

#
#  Main settings
# ..........................

SECRET_KEY = "change_this_key_with_a_value_of_your_choice"

ROOT_URL = ""
FORCE_SCRIPT_NAME = ROOT_URL if ROOT_URL != '' else None
ADMIN_MEDIA_PREFIX = '%s/static/admin/' % ROOT_URL
# Keep default values equal to buildout default values
STATIC_URL = '%s%s' % (ROOT_URL, "/static/")
MEDIA_URL = '%s%s' % (ROOT_URL, "/media/")
MEDIA_ROOT = os.path.join(DEPLOY_ROOT, 'var', 'media')
STATIC_ROOT = os.path.join(DEPLOY_ROOT, 'var', 'static')
CACHE_ROOT = os.path.join(DEPLOY_ROOT, 'var', 'cache')
MAPENTITY_CONFIG['TEMP_DIR'] = os.path.join(DEPLOY_ROOT, 'var', 'tmp')
SYNC_RANDO_ROOT = os.path.join(DEPLOY_ROOT, 'data')

MAILALERTSUBJECT = "Geotrek : Signal a mistake"
MAILALERTMESSAGE = "Hello, \n We acknowledge receipt of your feedback, thank you for your interest in Geotrek. \n " \
                   "Best regards, \n\nThe Geotrek Team\nhttp://www.geotrek.fr"

DATABASES['default']['NAME'] = "geotrekdb"
DATABASES['default']['USER'] = "geotrek"
DATABASES['default']['PASSWORD'] = "geotrek"
DATABASES['default']['HOST'] = 'localhost'
DATABASES['default']['PORT'] = 5432


CACHES['default']['TIMEOUT'] = 28800
CACHES['fat']['BACKEND'] = 'django.core.cache.backends.filebased.FileBasedCache'
CACHES['fat']['LOCATION'] = CACHE_ROOT
CACHES['fat']['TIMEOUT'] = 28800


LANGUAGE_CODE = "fr"
MODELTRANSLATION_DEFAULT_LANGUAGE = LANGUAGE_CODE
_MODELTRANSLATION_LANGUAGES = [l for l in LANGUAGES_LIST
                               if l[0] in ("en","fr","it","es")]

MODELTRANSLATION_LANGUAGES = [l[0] for l in _MODELTRANSLATION_LANGUAGES]
TITLE = "Geotrek"
MAPENTITY_CONFIG['TITLE'] = TITLE
MAPENTITY_CONFIG['ROOT_URL'] = ROOT_URL
MAPENTITY_CONFIG['LANGUAGE_CODE'] = LANGUAGE_CODE
MAPENTITY_CONFIG['LANGUAGES'] = LANGUAGES
MAPENTITY_CONFIG['TRANSLATED_LANGUAGES'] = _MODELTRANSLATION_LANGUAGES

EMAIL_SUBJECT_PREFIX = '[%s] ' % TITLE

#
# Deployment settings
# ..........................

MAPENTITY_CONFIG['CONVERSION_SERVER'] = 'http://127.0.0.1:6543'
MAPENTITY_CONFIG['CAPTURE_SERVER'] = 'http://127.0.0.1:8001'
TEMPLATES[1]['DIRS'] = (os.path.join(DEPLOY_ROOT, 'geotrek', 'templates'),
                        os.path.join(DEPLOY_ROOT, 'lib', 'parts', 'omelette',
                                     'mapentity', 'templates'),
                        os.path.join(MEDIA_ROOT, 'templates')) + TEMPLATES[1]['DIRS']


#
# Geotrek settings
# ..........................

DEFAULT_STRUCTURE_NAME = 'PNX'

#
# GIS settings
# ..........................


def api_bbox(bbox, buffer):
    wkt_box = 'POLYGON(({0} {1}, {2} {1}, {2} {3}, {0} {3}, {0} {1}))'
    wkt = wkt_box.format(*bbox)
    native = fromstr(wkt, srid=SRID)
    native.transform(API_SRID)
    extent = native.extent
    width = extent[2] - extent[0]
    native = native.buffer(width * buffer)
    return tuple(native.extent)


SRID = 2154
SPATIAL_EXTENT = 105000.0, 6150000.0, 1100000.0, 7150000.0

LEAFLET_CONFIG['TILES_EXTENT'] = SPATIAL_EXTENT
LEAFLET_CONFIG['SPATIAL_EXTENT'] = api_bbox(SPATIAL_EXTENT, VIEWPORT_MARGIN)

MAP_STYLES['path']['color'] = "#FF4800"
MAP_STYLES['city']['color'] = "#FF9700"
MAP_STYLES['district']['color'] = "#FF9700"

MAP_STYLES.setdefault('detail', {})['color'] = "#ffff00"
MAP_STYLES.setdefault('others', {})['color'] = "#ffff00"

FACEBOOK_APP_ID = ''
FACEBOOK_IMAGE = '/images/logo-geotrek.png'
FACEBOOK_IMAGE_WIDTH = 200
FACEBOOK_IMAGE_HEIGHT = 200
