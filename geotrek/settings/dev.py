from .base import * #noqa
from django.conf.global_settings import LANGUAGES as LANGUAGES_LIST

#
# Django Development
# ..........................

DEBUG = True

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

#
# Developper additions
# ..........................

INSTALLED_APPS = (
    'django_extensions',
    'debug_toolbar',
) + INSTALLED_APPS

INTERNAL_IPS = type(str('c'), (), {'__contains__': lambda *a: True})()

ALLOWED_HOSTS = [
    '*',
]

MIDDLEWARE_CLASSES += (
    'debug_toolbar.middleware.DebugToolbarMiddleware',
)
#
# Use some default tiles
# ..........................

LOGGING['loggers']['geotrek']['level'] = 'DEBUG'
LOGGING['loggers']['']['level'] = 'DEBUG'

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
