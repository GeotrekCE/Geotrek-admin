import os
from .base import *
from django.conf.global_settings import LANGUAGES as LANGUAGES_LIST

#
# Django Production
# ..........................
ALLOWED_HOSTS = [
    os.getenv('DOMAIN_NAME'),
]

USE_X_FORWARDED_HOST = True
COMPRESS_ENABLED = True


CACHES['default']['BACKEND'] = 'django.core.cache.backends.memcached.MemcachedCache'
CACHES['default']['LOCATION'] = '{}:{}'.format(os.getenv('MEMCACHED_HOST', 'memcached'),
                                               os.getenv('MEMCACHED_PORT', '11211'))

LOGGING['handlers']['mail_admins']['class'] = 'django.utils.log.AdminEmailHandler'
LOGGING['handlers']['logfile'] = {'class': 'logging.FileHandler',
                                  'formatter': 'simple',
                                  'filename': os.path.join(VAR_DIR, 'log', 'geotrek.log')}

LOGGING['loggers']['geotrek']['handlers'].append('logfile')
LOGGING['loggers']['mapentity']['handlers'].append('logfile')

try:
    from .custom import *  # NOQA
except ImportError:
    pass

# force reloading data in custom.py
_MODELTRANSLATION_LANGUAGES = [l for l in LANGUAGES_LIST
                               if l[0] in MODELTRANSLATION_LANGUAGES]

LEAFLET_CONFIG['TILES_EXTENT'] = SPATIAL_EXTENT
LEAFLET_CONFIG['SPATIAL_EXTENT'] = api_bbox(SPATIAL_EXTENT, VIEWPORT_MARGIN)
MAPENTITY_CONFIG['TRANSLATED_LANGUAGES'] = _MODELTRANSLATION_LANGUAGES
MAPENTITY_CONFIG['LANGUAGE_CODE'] = LANGUAGE_CODE
