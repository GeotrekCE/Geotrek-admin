from .base import *  # noqa


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

SECRET_KEY = "Ceci n'est pas du tout secret mais c'est juste pour le dev"

DEBUG_TOOLBAR = False

INTERNAL_IPS += ('10.0.3.1',)


if DEBUG_TOOLBAR:
    INSTALLED_APPS = (
        'debug_toolbar',
    ) + INSTALLED_APPS

    MIDDLEWARE_CLASSES += (
        'debug_toolbar.middleware.DebugToolbarMiddleware',
    )
