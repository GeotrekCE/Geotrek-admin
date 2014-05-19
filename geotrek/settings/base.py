import os
import sys

from django.contrib.messages import constants as messages

from geotrek import __version__
from . import PROJECT_ROOT_PATH

gettext_noop = lambda s: s


DEBUG = False
TEMPLATE_DEBUG = DEBUG
TEST = 'test' in sys.argv
VERSION = __version__

ADMINS = (
    ('Makina Corpus', 'geobi@makina-corpus.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': '',                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

AUTHENTICATION_BACKENDS = ('django.contrib.auth.backends.ModelBackend',)
AUTH_PROFILE_MODULE = 'authent.UserProfile'

# Settings required for geotrek.authent.backend.DatabaseBackend :
AUTHENT_DATABASE = None
AUTHENT_TABLENAME = None
AUTHENT_GROUPS_MAPPING = {
    'PATH_MANAGER': 1,
    'TREKKING_MANAGER': 2,
    'EDITOR': 3,
    'READER': 4,
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Paris'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'fr'

MODELTRANSLATION_DEFAULT_LANGUAGE = LANGUAGE_CODE


LANGUAGES = (
    ('en', gettext_noop('English')),
    ('fr', gettext_noop('French')),
    ('it', gettext_noop('Italian')),
    ('es', gettext_noop('Spanish')),
)

LOCALE_PATHS = (
    os.path.join(PROJECT_ROOT_PATH, 'locale'),
)

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

DATE_INPUT_FORMATS = ('%d/%m/%Y',)

ROOT_URL = ''
LOGIN_URL = 'login'
LOGOUT_URL = 'logout'
LOGIN_REDIRECT_URL = 'home'

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = os.path.join(PROJECT_ROOT_PATH, 'media')

UPLOAD_DIR = 'upload'    # media root subdir

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'
MEDIA_URL_SECURE = '/media_secure/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = ''

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    os.path.join(PROJECT_ROOT_PATH, 'static'),
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    #'django.contrib.staticfiles.finders.DefaultStorageFinder',
    'compressor.finders.CompressorFinder',
)

STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

COMPRESSOR_ENABLED = False
COMPRESS_PARSER = 'compressor.parser.HtmlParser'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'public_key'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    # 'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'geotrek.authent.middleware.LocaleForcedMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'mapentity.middleware.AutoLoginMiddleware'
)

ROOT_URLCONF = 'geotrek.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'geotrek.wsgi.application'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.tz',
    'django.core.context_processors.request',
    'django.contrib.messages.context_processors.messages',

    'mapentity.context_processors.settings',
)

#
# /!\ Application names (last levels) must be unique
# (c.f. auth/authent)
# https://code.djangoproject.com/ticket/12288
#
PROJECT_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.gis',
)


# Do not migrate translated fields, they differ per instance, and
# can be added/removed using `update_translation_fields`
if 'schemamigration' not in sys.argv:
    PROJECT_APPS += ('modeltranslation',)


PROJECT_APPS += (
    'south',
    'leaflet',
    'floppyforms',
    'crispy_forms',
    'compressor',
    'djgeojson',
    'tinymce',
    'easy_thumbnails',
    'shapes',
    'paperclip',
    'mapentity',
)


INSTALLED_APPS = PROJECT_APPS + (
    'geotrek.authent',
    'geotrek.common',
    'geotrek.altimetry',
    'geotrek.core',
    'geotrek.infrastructure',
    'geotrek.maintenance',
    'geotrek.zoning',
    'geotrek.land',
    'geotrek.trekking',
    'geotrek.tourism',
    'geotrek.feedback',
)

SERIALIZATION_MODULES = {
    'geojson': 'djgeojson.serializers'
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    },
    # The fat backend is used to store big chunk of data (>1 Mo)
    'fat': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'formatters': {
        'simple': {
            'format': '%(levelname)s %(asctime)s %(name)s %(message)s'
        },
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'logging.NullHandler'
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
    },
    'loggers': {
        'django.db.backends': {
            'handlers': ['console', 'mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console', 'mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django': {
            'handlers': ['console', 'mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },
        'south': {
            'handlers': ['console', 'mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },
        'geotrek': {
            'handlers': ['console', 'mail_admins'],
            'level': 'INFO',
            'propagate': False,
        },
        'mapentity': {
            'handlers': ['console', 'mail_admins'],
            'level': 'INFO',
            'propagate': False,
        },
        '': {
            'handlers': ['console', 'mail_admins'],
            'level': 'INFO',
            'propagate': False,
        },
    }
}

THUMBNAIL_ALIASES = {
    '': {
        'thumbnail': {'size': (150, 150)},
        # Thumbnails for public trek website
        'small-square': {'size': (120, 120), 'crop': True},
        'medium': {'size': (500, 500)},
        'print': {'size': (1000, 500), 'crop': 'smart'},
    },
}


PAPERCLIP_CONFIG = {
    'FILETYPE_MODEL': 'common.FileType',
    'ATTACHMENT_TABLE_NAME': 'fl_t_fichier',
}


# Data projection
SRID = 3857

# API projection (client-side), can differ from SRID (database). Leaflet requires 4326.
API_SRID = 4326

# Extent in native projection (Toulouse area)
SPATIAL_EXTENT = (144968, 5415668, 175412, 5388753)


MAPENTITY_CONFIG = {
    'TITLE': gettext_noop("Geotrek"),
    'TEMP_DIR': '/tmp',
    'HISTORY_ITEMS_MAX': 7,
    'CONVERSION_SERVER': 'http://127.0.0.1:6543',
    'CAPTURE_SERVER': 'http://127.0.0.1:8001',
    'ROOT_URL': ROOT_URL,
    'MAP_BACKGROUND_FOGGED': True,
    'GEOJSON_LAYERS_CACHE_BACKEND': 'fat'
}

DEFAULT_STRUCTURE_NAME = gettext_noop('Default')

SNAP_DISTANCE = 30  # Distance of snapping in pixels

ALTIMETRIC_PROFILE_PRECISION = 25  # Sampling precision in meters
ALTIMETRIC_PROFILE_BACKGROUND = 'white'
ALTIMETRIC_PROFILE_COLOR = '#F77E00'
ALTIMETRIC_PROFILE_HEIGHT = 400
ALTIMETRIC_PROFILE_WIDTH = 800
ALTIMETRIC_PROFILE_FONTSIZE = 25
ALTIMETRIC_AREA_MAX_RESOLUTION = 150  # Maximum number of points (by width/height)


# Let this be defined at instance-level
LEAFLET_CONFIG = {
    'SRID': SRID,
    'TILES': [
        ('Scan', 'http://{s}.tiles.openstreetmap.org/{z}/{x}/{y}.png',),
        ('Ortho', 'http://{s}.tiles.openstreetmap.org/{z}/{x}/{y}.jpg'),
    ],
    'TILES_EXTENT': SPATIAL_EXTENT,
    # Extent in API projection (Leaflet view default extent)
    'SPATIAL_EXTENT': (1.3, 43.7, 1.5, 43.5),
    'NO_GLOBALS': False,
    'PLUGINS': {
        'topofields': {'js': ['core/geotrek.forms.snap.js',
                              'core/geotrek.forms.topology.js',
                              'core/dijkstra.js',
                              'core/multipath.js',
                              'core/topology_helper.js']}
    }
}

""" This *pool* of colors is used to colorized lands records.
"""
LAND_COLORS_POOL = {'land': ['#f37e79', '#7998f3', '#bbf379', '#f379df', '#f3bf79', '#9c79f3', '#7af379'],
                    'physical': ['#f3799d', '#79c1f3', '#e4f379', '#de79f3', '#79f3ba', '#f39779', '#797ff3'],
                    'competence': ['#a2f379', '#f379c6', '#79e9f3', '#f3d979', '#b579f3', '#79f392', '#f37984'],
                    'signagemanagement': ['#79a8f3', '#cbf379', '#f379ee', '#79f3e3', '#79f3d3'],
                    'workmanagement': ['#79a8f3', '#cbf379', '#f379ee', '#79f3e3', '#79f3d3']}

MAP_STYLES = {
    'path':           {'weight': 2, 'opacity': 1.0, 'color': '#FF4800'},

    'city':           {'weight': 4, 'color': 'orange', 'opacity': 0.3, 'fillOpacity': 0.0},
    'district':       {'weight': 4, 'color': 'orange', 'opacity': 0.3, 'fillOpacity': 0.0},
    'restrictedarea': {'weight': 4, 'color': 'orange', 'opacity': 0.3, 'fillOpacity': 0.0},

    'land':              {'weight': 4, 'color': 'red', 'opacity': 1.0},
    'physical':          {'weight': 6, 'color': 'red', 'opacity': 1.0},
    'competence':        {'weight': 4, 'color': 'red', 'opacity': 1.0},
    'workmanagement':    {'weight': 4, 'color': 'red', 'opacity': 1.0},
    'signagemanagement': {'weight': 5, 'color': 'red', 'opacity': 1.0},
}


LAYER_PRECISION_LAND = 4   # Number of fraction digit
LAYER_SIMPLIFY_LAND = 10  # Simplification tolerance

LAND_BBOX_CITIES_ENABLED = True
LAND_BBOX_DISTRICTS_ENABLED = True
LAND_BBOX_AREAS_ENABLED = False

TREK_COMPLETENESS_FIELDS = ['departure', 'duration', 'difficulty',
                            'description_teaser']
TREK_DAY_DURATION = 10  # Max duration to be done in one day

# Static offsets in projection units
TOPOLOGY_STATIC_OFFSETS = {'land': -5,
                           'physical': 0,
                           'competence': 5,
                           'signagemanagement': -10,
                           'workmanagement': 10}

MESSAGE_TAGS = {
    messages.SUCCESS: 'alert-success',
    messages.INFO: 'alert-info',
    messages.DEBUG: 'alert-info',
    messages.WARNING: 'alert-error',
    messages.ERROR: 'alert-error',
}
