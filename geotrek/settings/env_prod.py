import os

#
# Django Production
# ..........................

USE_X_FORWARDED_HOST = True
COMPRESS_ENABLED = True


CACHES['default']['BACKEND'] = 'django.core.cache.backends.memcached.PyMemcacheCache'
CACHES['default']['LOCATION'] = '{}:{}'.format(os.getenv('MEMCACHED_HOST', 'memcached'),
                                               os.getenv('MEMCACHED_PORT', '11211'))

LOGGING['handlers']['mail_admins']['class'] = 'django.utils.log.AdminEmailHandler'
LOGGING['handlers']['logfile'] = {'class': 'logging.FileHandler',
                                  'formatter': 'simple',
                                  'filename': os.path.join(VAR_DIR, 'log', 'geotrek.log')}

LOGGING['loggers']['geotrek']['handlers'].append('logfile')
LOGGING['loggers']['mapentity']['handlers'].append('logfile')
