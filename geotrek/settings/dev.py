from .default import *

#
# Django Development
# ..........................

DEBUG = True
TEMPLATES[1]['OPTIONS']['debug'] = True
DEBUG_TOOLBAR = False

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

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

try:
    from .local import *  # NOQA
    # set local settings for dev
except ImportError:
    pass
