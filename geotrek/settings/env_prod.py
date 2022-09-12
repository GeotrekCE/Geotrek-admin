import os

#
# Django Production
# ..........................

USE_X_FORWARDED_HOST = True
COMPRESS_ENABLED = True


CACHES['default']['BACKEND'] = 'django.core.cache.backends.memcached.PyMemcacheCache'
CACHES['default']['LOCATION'] = '{}:{}'.format(os.getenv('MEMCACHED_HOST', 'memcached'),
                                               os.getenv('MEMCACHED_PORT', '11211'))

LOGGING['loggers']['']['handlers'] = ('mail_admins', 'console', 'log_file')
