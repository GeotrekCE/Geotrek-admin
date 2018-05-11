from .base import *

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
    # set local settings for dev
except ImportError:
    pass
