import os
import sys

from django.contrib.messages import constants as messages


gettext_noop = lambda s: s

PROJECT_ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

DEBUG = True
TEMPLATE_DEBUG = DEBUG
TEST = 'test' in sys.argv

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

# Settings required for caminae.authent.backend.DatabaseBackend : 
AUTHENT_DATABASE = None
AUTHENT_TABLENAME = None

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

MODELTRANSLATION_TRANSLATION_REGISTRY = 'caminae.translation'

LANGUAGES = (
    ('en', gettext_noop('English')),
    ('fr', gettext_noop('French')),
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

ROOT_URL = '/'
LOGIN_URL = '/login/'
LOGOUT_URL = '/logout/'
LOGIN_REDIRECT_URL = '/'

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = ''

UPLOAD_DIR = 'upload'    # media root subdir

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

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

# Make this unique, and don't share it with anybody.
SECRET_KEY = '4b1f@)*y$hobaevq9j&amp;hdph%&amp;!go0ud1qn0a)2&amp;l$np*el3uj&amp;'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    # 'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'caminae.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'caminae.wsgi.application'

TEMPLATE_DIRS = (
    os.path.join(PROJECT_ROOT_PATH, 'templates'),
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

    'caminae.common.context_processors.settings',
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
#    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.gis',

    'south',
    'modeltranslation',
    'leaflet',
    'floppyforms',
    'crispy_forms',
    'compressor',
    'djgeojson',
    'tinymce',
    'easy_thumbnails',
    'shapes',
)

INSTALLED_APPS = PROJECT_APPS + (
    'caminae.authent',
    'caminae.common',
    'caminae.core',
    'caminae.maintenance',
    'caminae.land',
    'caminae.trekking',
    'caminae.infrastructure',
    'caminae.mapentity',
    'caminae.paperclip',
)

SERIALIZATION_MODULES = {
    'geojson' : 'djgeojson.serializers'
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
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'console':{
            'level':'DEBUG',
            'class':'logging.StreamHandler',
            'formatter': 'simple'
        },
    },
    'loggers': {
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
        'caminae': {
            'handlers': ['console', 'mail_admins'],
            'level': 'WARNING',
            'propagate': False,
        },
        '': {
            'handlers': ['console', 'mail_admins'],
            'level': 'WARNING',
            'propagate': False,
        },
    }
}

THUMBNAIL_ALIASES = {
    '': {
        'thumbnail': {'size': (150, 150)},
    },
}

SCREAMSHOT_CONFIG = {
    'CAPTURE_ALLOWED_IPS': ('127.0.0.1',),
}


TITLE = gettext_noop("Caminae")
DEFAULT_STRUCTURE_NAME = None
SRID = None
SPATIAL_EXTENT = None

# API projection (client-side), can differ from SRID (database)
API_SRID = 4326

SNAP_DISTANCE = 30  # Distance of snapping in pixels

# Let this be defined at instance-level
LEAFLET_CONFIG = {
    'TILES_URL' : [],
    'TILES_EXTENT' : None,
    'SPATIAL_EXTENT' : None
}

LAYERCOLOR_PATHS = ''      # Hex color for paths
LAYERCOLOR_LAND = ''       # Hex color for land layers
LAYERCOLOR_OTHERS = ''     # Hex color for entity layers
LAYER_PRECISION_LAND = 4   # Number of fraction digit
LAYER_SIMPLIFY_LAND  = 10  # Simplification tolerance


# Navigation history tabs
HISTORY_ITEMS_MAX = 7

MESSAGE_TAGS = {
    messages.SUCCESS: 'alert-success',
    messages.INFO: 'alert-info',
    messages.DEBUG: 'alert-info',
    messages.WARNING: 'alert-error',
    messages.ERROR: 'alert-error',
}

CONVERSION_SERVER = None   # URL of PDF conversion server
