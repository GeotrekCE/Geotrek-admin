import os
import sys
import djcelery

from django.contrib.messages import constants as messages

from geotrek import __version__
from . import PROJECT_ROOT_PATH


def gettext_noop(s):
    return s


DEBUG = False
TEST = 'test' in sys.argv
VERSION = __version__

ADMINS = (
    ('Makina Corpus', 'geobi@makina-corpus.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'OPTIONS': {},
        'NAME': '',                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
        'TEST': {
            'SERIALIZE': False,
        },
    }
}

#
# PostgreSQL Schemas for apps and models.
#
# Caution: editing this setting might not be enough.
# Indeed, it won't apply to apps that not managed of South, nor database views and functions.
# See all sql/*-schemas.sql files in each Geotrek app.
#
DATABASE_SCHEMAS = {
    'default': 'geotrek',
    'gis': 'public',
    'auth': 'django',
    'django': 'django',
    'easy_thumbnails': 'django',
    'feedback': 'gestion',
    'infrastructure': 'gestion',
    'maintenance': 'gestion',
    'tourism': 'tourisme',
    'trekking': 'rando',
    'zoning': 'zonage',
    'land': 'foncier',
}

DATABASES['default']['OPTIONS'] = {
    'options': '-c search_path=public,%s' % ','.join(set(DATABASE_SCHEMAS.values()))
}

#
# Authentication
#
AUTHENTICATION_BACKENDS = ('django.contrib.auth.backends.ModelBackend',)

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
    # 'django.contrib.staticfiles.finders.DefaultStorageFinder',
    'compressor.finders.CompressorFinder',
)

STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

COMPRESSOR_ENABLED = False
COMPRESS_PARSER = 'compressor.parser.HtmlParser'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'public_key'

TEMPLATES = [
    {
        'BACKEND': 'djappypod.backend.OdtTemplates',
    },
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': (),
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.core.context_processors.debug',
                'django.core.context_processors.i18n',
                'django.core.context_processors.media',
                'django.core.context_processors.static',
                'django.core.context_processors.tz',
                'django.core.context_processors.request',
                'django.contrib.messages.context_processors.messages',
                'geotrek.context_processors.forced_layers',
                'mapentity.context_processors.settings',
            ],
            'loaders': [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
                'geotrek.templateloaders.Loader',
                # 'django.template.loaders.eggs.Loader',
            ],
            'debug': True,
        },
    },
]

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'geotrek.authent.middleware.LocaleForcedMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'geotrek.common.middleware.APILocaleMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'geotrek.authent.middleware.CorsMiddleware',
    'mapentity.middleware.AutoLoginMiddleware'
)

ROOT_URLCONF = 'geotrek.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'geotrek.wsgi.application'


# Do not migrate translated fields, they differ per instance, and
# can be added/removed using `update_translation_fields`
# modeltranslation should be kept before django.contrib.admin
if 'makemigrations' in sys.argv:
    PROJECT_APPS = ()
else:
    PROJECT_APPS = (
        'modeltranslation',
    )

#
# /!\ Application names (last levels) must be unique
# (c.f. auth/authent)
# https://code.djangoproject.com/ticket/12288
#
PROJECT_APPS += (
    'geotrek.appconfig.AuthGeotrekConfig',  # django.contrib.app
    'geotrek.appconfig.ContenttypeGeotrekConfig',  # django.contrib.contenttypes
    'geotrek.appconfig.SessionsGeotrekConfig',  # django.contrib.sessions
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'geotrek.appconfig.AdminGeotrekConfig',   # django.contrib.admin
    'django.contrib.admindocs',
    'django.contrib.gis',
)


PROJECT_APPS += (
    'floppyforms',
    'crispy_forms',
    'compressor',
    'djgeojson',
    'django_filters',
    'tinymce',
    'geotrek.appconfig.EasyThumbnailsGeotrekConfig',  # easy_thumbnails
    'shapes',
    'paperclip',
    'mapentity',
    'leaflet',  # After mapentity to allow it to patch settings
    'rest_framework',
    'rest_framework_gis',
    'rest_framework_swagger',
    'embed_video',
    'geotrek.appconfig.CeleryGeotrekConfig',  # djcelery
)


INSTALLED_APPS = PROJECT_APPS + (
    'geotrek.cirkwi',
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
    'geotrek.flatpages',
    'geotrek.feedback',
    'geotrek.api',
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
            'level': 'WARNING',
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
        'medium': {'size': (800, 800)},
        # Header image for trek export (keep ratio of TREK_EXPORT_HEADER_IMAGE_SIZE)
        'print': {'size': (1000, 500), 'crop': 'smart'},
    },
}


PAPERCLIP_ENABLE_VIDEO = True
PAPERCLIP_ENABLE_LINK = True
PAPERCLIP_FILETYPE_MODEL = 'common.FileType'
PAPERCLIP_ATTACHMENT_MODEL = 'common.Attachment'


# Data projection
SRID = 2154  # Lambert-93 for Metropolitan France

# API projection (client-side), can differ from SRID (database). Leaflet requires 4326.
API_SRID = 4326

# Extent in native projection (Toulouse area)
SPATIAL_EXTENT = (105000, 6150000, 1100000, 7150000)


MAPENTITY_CONFIG = {
    'TITLE': gettext_noop("Geotrek"),
    'TEMP_DIR': '/tmp',
    'HISTORY_ITEMS_MAX': 7,
    'CONVERSION_SERVER': 'http://127.0.0.1:6543',
    'CAPTURE_SERVER': 'http://127.0.0.1:8001',
    'ROOT_URL': ROOT_URL,
    'MAP_BACKGROUND_FOGGED': True,
    'GEOJSON_LAYERS_CACHE_BACKEND': 'fat',
    'SENDFILE_HTTP_HEADER': 'X-Accel-Redirect',
    'DRF_API_URL_PREFIX': r'^api/(?P<lang>\w+)/',
    'MAPENTITY_WEASYPRINT': False,
}

DEFAULT_STRUCTURE_NAME = gettext_noop('Default')

VIEWPORT_MARGIN = 0.1  # On list page, around spatial extent from settings.ini

PATHS_LINE_MARKER = 'dotL'
PATH_SNAPPING_DISTANCE = 1  # Distance of path snapping in meters
SNAP_DISTANCE = 30  # Distance of snapping in pixels
PATH_MERGE_SNAPPING_DISTANCE = 2  # minimum distance to merge paths

ALTIMETRIC_PROFILE_PRECISION = 25  # Sampling precision in meters
ALTIMETRIC_PROFILE_AVERAGE = 2  # nb of points for altimetry moving average
ALTIMETRIC_PROFILE_STEP = 1  # Step min precision for positive / negative altimetry gain
ALTIMETRIC_PROFILE_BACKGROUND = 'white'
ALTIMETRIC_PROFILE_COLOR = '#F77E00'
ALTIMETRIC_PROFILE_HEIGHT = 400
ALTIMETRIC_PROFILE_WIDTH = 800
ALTIMETRIC_PROFILE_FONTSIZE = 25
ALTIMETRIC_PROFILE_FONT = 'ubuntu'
ALTIMETRIC_PROFILE_MIN_YSCALE = 1200  # Minimum y scale (in meters)
ALTIMETRIC_AREA_MAX_RESOLUTION = 150  # Maximum number of points (by width/height)
ALTIMETRIC_AREA_MARGIN = 0.15


# Let this be defined at instance-level
LEAFLET_CONFIG = {
    'SRID': 3857,
    'TILES': [
        ('OSM', 'http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', '(c) OpenStreetMap Contributors'),
        ('OSM N&B', 'http://{s}.tiles.wmflabs.org/bw-mapnik/{z}/{x}/{y}.png', '(c) OpenStreetMap Contributors'),
    ],
    'TILES_EXTENT': SPATIAL_EXTENT,
    # Extent in API projection (Leaflet view default extent)
    'SPATIAL_EXTENT': (1.3, 43.7, 1.5, 43.5),
    'NO_GLOBALS': False,
    'PLUGINS': {
        'geotrek': {'js': ['core/leaflet.lineextremities.js',
                           'core/leaflet.textpath.js',
                           'trekking/points_reference.js',
                           'trekking/parking_location.js']},
        'topofields': {'js': ['core/geotrek.forms.snap.js',
                              'core/geotrek.forms.topology.js',
                              'core/dijkstra.js',
                              'core/multipath.js',
                              'core/topology_helper.js']}
    }
}

# define forced layers from LEAFLET_CONFIG when map center in polygon
# [('Scan', [(lat1, lng1), (lat2, lng2), (lat3, lng3), (lat4, lng4), (lat1, lng1)]),]
FORCED_LAYERS = []

""" This *pool* of colors is used to colorized lands records.
"""
COLORS_POOL = {'land': ['#f37e79', '#7998f3', '#bbf379', '#f379df', '#f3bf79', '#9c79f3', '#7af379'],
               'physical': ['#f3799d', '#79c1f3', '#e4f379', '#de79f3', '#79f3ba', '#f39779', '#797ff3'],
               'competence': ['#a2f379', '#f379c6', '#79e9f3', '#f3d979', '#b579f3', '#79f392', '#f37984'],
               'signagemanagement': ['#79a8f3', '#cbf379', '#f379ee', '#79f3e3', '#79f3d3'],
               'workmanagement': ['#79a8f3', '#cbf379', '#f379ee', '#79f3e3', '#79f3d3'],
               'restrictedarea': ['plum', 'violet', 'deeppink', 'orchid',
                                  'darkviolet', 'lightcoral', 'palevioletred',
                                  'MediumVioletRed', 'MediumOrchid', 'Magenta',
                                  'LightSalmon', 'HotPink', 'Fuchsia']}

MAP_STYLES = {
    'path': {'weight': 2, 'opacity': 1.0, 'color': '#FF4800'},

    'city': {'weight': 4, 'color': 'orange', 'opacity': 0.3, 'fillOpacity': 0.0},
    'district': {'weight': 6, 'color': 'orange', 'opacity': 0.3, 'fillOpacity': 0.0, 'dashArray': '12, 12'},

    'restrictedarea': {'weight': 2, 'color': 'red', 'opacity': 0.5, 'fillOpacity': 0.5},
    'land': {'weight': 4, 'color': 'red', 'opacity': 1.0},
    'physical': {'weight': 6, 'color': 'red', 'opacity': 1.0},
    'competence': {'weight': 4, 'color': 'red', 'opacity': 1.0},
    'workmanagement': {'weight': 4, 'color': 'red', 'opacity': 1.0},
    'signagemanagement': {'weight': 5, 'color': 'red', 'opacity': 1.0},

    'print': {
        'path': {'weight': 1},
        'trek': {'color': '#FF3300', 'weight': 7, 'opacity': 0.5,
                 'arrowColor': 'black', 'arrowSize': 10},
    }
}


LAYER_PRECISION_LAND = 4   # Number of fraction digit
LAYER_SIMPLIFY_LAND = 10  # Simplification tolerance

LAND_BBOX_CITIES_ENABLED = True
LAND_BBOX_DISTRICTS_ENABLED = True
LAND_BBOX_AREAS_ENABLED = False

PUBLISHED_BY_LANG = True

EXPORT_MAP_IMAGE_SIZE = {
    'trek': (18.2, 18.2),
    'poi': (18.2, 18.2),
    'touristiccontent': (18.2, 18.2),
    'touristicevent': (18.2, 18.2),
}

EXPORT_HEADER_IMAGE_SIZE = {
    'trek': (10.7, 5.35),  # Keep ratio of THUMBNAIL_ALIASES['print']
    'poi': (10.7, 5.35),  # Keep ratio of THUMBNAIL_ALIASES['print']
    'touristiccontent': (10.7, 5.35),  # Keep ratio of THUMBNAIL_ALIASES['print']
    'touristicevent': (10.7, 5.35),  # Keep ratio of THUMBNAIL_ALIASES['print']
}

COMPLETENESS_FIELDS = {
    'trek': ['departure', 'duration', 'difficulty', 'description_teaser']
}

TRAIL_MODEL_ENABLED = True
TREKKING_TOPOLOGY_ENABLED = True
FLATPAGES_ENABLED = True
TOURISM_ENABLED = True

TREK_POI_INTERSECTION_MARGIN = 500  # meters (used only if TREKKING_TOPOLOGY_ENABLED = False)
TOURISM_INTERSECTION_MARGIN = 500  # meters (always used)

SIGNAGE_LINE_ENABLED = False

TREK_POINTS_OF_REFERENCE_ENABLED = True
TREK_EXPORT_POI_LIST_LIMIT = 14
TREK_EXPORT_INFORMATION_DESK_LIST_LIMIT = 2

TREK_ICON_SIZE_POI = 18
TREK_ICON_SIZE_SERVICE = 18
TREK_ICON_SIZE_PARKING = 18
TREK_ICON_SIZE_INFORMATION_DESK = 18

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

CACHE_TIMEOUT_LAND_LAYERS = 60 * 60 * 24

TREK_CATEGORY_ORDER = None
TOURISTIC_EVENT_CATEGORY_ORDER = None
SPLIT_TREKS_CATEGORIES_BY_PRACTICE = False
SPLIT_TREKS_CATEGORIES_BY_ACCESSIBILITY = False
HIDE_PUBLISHED_TREKS_IN_TOPOLOGIES = False
ZIP_TOURISTIC_CONTENTS_AS_POI = False

CRISPY_ALLOWED_TEMPLATE_PACKS = ('bootstrap', 'bootstrap3')
CRISPY_TEMPLATE_PACK = 'bootstrap'

# Mobile app_directories
MOBILE_TILES_URL = [
    'http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
]
MOBILE_TILES_EXTENSION = None  # auto
MOBILE_TILES_RADIUS_LARGE = 0.01  # ~1 km
MOBILE_TILES_RADIUS_SMALL = 0.005  # ~500 m
MOBILE_TILES_GLOBAL_ZOOMS = range(13)
MOBILE_TILES_LOW_ZOOMS = range(13, 15)
MOBILE_TILES_HIGH_ZOOMS = range(15, 17)

djcelery.setup_loader()

CELERY_RESULT_BACKEND = 'djcelery.backends.database:DatabaseBackend'
BROKER_URL = 'redis://127.0.0.1:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TASK_RESULT_EXPIRES = 5
CELERYD_TASK_TIME_LIMIT = 10800
CELERYD_TASK_SOFT_TIME_LIMIT = 21600
TEST_RUNNER = 'djcelery.contrib.test_runner.CeleryTestSuiteRunner'

TINYMCE_DEFAULT_CONFIG = {
    'convert_urls': False,
}

SYNC_RANDO_OPTIONS = {}

'''
If true; displays the attached pois pictures in the Trek's geojson pictures property.
In Geotrek Rando it enables correlated pictures to be displayed in the slideshow.
'''
TREK_WITH_POIS_PICTURES = False

SWAGGER_SETTINGS = {
    'USE_SESSION_AUTH': False,
    'APIS_SORTER': 'alpha',
    'JSON_EDITOR': True
}
