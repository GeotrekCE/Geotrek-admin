from .base import *

#
# Django Development
# ..........................

DEBUG = True
DEBUG_TOOLBAR = False

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

#
# Developper additions
# ..........................

INSTALLED_APPS = (
    'django_extensions',
) + INSTALLED_APPS

INTERNAL_IPS = (
    '127.0.0.1',  # localhost default
    '10.0.3.1',  # lxc default
)

ALLOWED_HOSTS = [
    '*',
]

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
