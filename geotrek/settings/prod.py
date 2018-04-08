import os

from .base import *  # noqa
from .base import INSTALLED_APPS, CACHES, LOGGING, DATABASES, VAR_ROOT

#
# Django Production
# ..........................

USE_X_FORWARDED_HOST = True

COMPRESSOR_ENABLED = True

INSTALLED_APPS += (
    'gunicorn',
)

CACHES['default']['BACKEND'] = 'django.core.cache.backends.memcached.MemcachedCache'
CACHES['default']['LOCATION'] = '127.0.0.1:11211'

LOGGING['handlers']['mail_admins']['class'] = 'django.utils.log.AdminEmailHandler'
LOGGING['handlers']['logfile'] = {'class': 'logging.FileHandler',
                                  'formatter': 'simple',
                                  'filename': os.path.join(VAR_ROOT, 'log', 'geotrek.log')}
LOGGING['loggers']['geotrek']['handlers'].append('logfile')
LOGGING['loggers']['mapentity']['handlers'].append('logfile')

#
# Optimizations
# ..........................

DATABASES['default']['CONN_MAX_AGE'] = 600

# Template caching is not compatible with MAPENTITY_CONFIG['MAPENTITY_WEASYPRINT'] = False
# TEMPLATES[1]['OPTIONS']['loaders'] = (
#     ('django.template.loaders.cached.Loader',
#      TEMPLATES[1]['OPTIONS']['loaders']),
# )

# SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
