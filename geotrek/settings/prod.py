import os
from .base import *

#
# Django Production
# ..........................

USE_X_FORWARDED_HOST = True
COMPRESS_ENABLED = True


CACHES['default']['BACKEND'] = 'django.core.cache.backends.memcached.MemcachedCache'
CACHES['default']['LOCATION'] = '127.0.0.1:11211'

LOGGING['handlers']['mail_admins']['class'] = 'django.utils.log.AdminEmailHandler'
LOGGING['handlers']['logfile'] = {'class': 'logging.FileHandler',
                                  'formatter': 'simple',
                                  'filename': os.path.join(PRIVATE_DIR, 'log', 'geotrek.log')}
LOGGING['loggers']['geotrek']['handlers'].append('logfile')
LOGGING['loggers']['mapentity']['handlers'].append('logfile')

try:
    from .custom import *  # NOQA

except ImportError:
    pass
