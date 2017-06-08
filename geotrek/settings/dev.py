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
)

ALLOWED_HOSTS = [
    '*',
]

#
# Use some default tiles
# ..........................

LEAFLET_CONFIG['TILES'] = [
    (gettext_noop('Scan'), 'http://{s}.tile.osm.org/{z}/{x}/{y}.png', '(c) OpenStreetMap Contributors'),
    (gettext_noop('Ortho'), 'http://{s}.tiles.mapbox.com/v3/openstreetmap.map-4wvf9l0l/{z}/{x}/{y}.jpg', '(c) MapBox'),
]
LEAFLET_CONFIG['OVERLAYS'] = [
    (gettext_noop('Coeur de parc'), 'http://{s}.tilestream.makina-corpus.net/v2/coeur-ecrins/{z}/{x}/{y}.png', 'Ecrins'),
]

LOGGING['loggers']['geotrek']['level'] = 'DEBUG'
LOGGING['loggers']['']['level'] = 'DEBUG'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

try:
    from .local import *  # NOQA
    # set local settings for dev
except ImportError:
    pass
