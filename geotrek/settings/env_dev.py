#
# Django Development
# ..........................

import sys
import os

# Makemessages uses Locale_paths's settings to get the list of translations to do.
# We change 'var/extra_locale' to 'geotrek/locale'

if 'makemessages' in sys.argv:
    LOCALE_PATHS = (os.path.join(PROJECT_DIR, 'locale'),)  # NoQA: F821

DEBUG = True

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

#
# Developper additions
# ..........................

INSTALLED_APPS = (
    'django_extensions',
    'debug_toolbar',
    'drf_yasg',
) + INSTALLED_APPS  # NoQA: F821

INTERNAL_IPS = type(str('c'), (), {'__contains__': lambda *a: True})()

ALLOWED_HOSTS = ['*']

MIDDLEWARE += (  # NoQA: F821
    'debug_toolbar.middleware.DebugToolbarMiddleware',
)
#
# Use some default tiles
# ..........................

LOGGING['loggers']['geotrek']['level'] = 'DEBUG'  # NoQA: F821
LOGGING['loggers']['']['level'] = 'DEBUG'  # NoQA: F821

SYNC_RANDO_OPTIONS = {
    'url': 'http://geotrek.local:8000'  # Mandatory for dev mode. Must point to the same domain than SERVER_NAME in .env
}
