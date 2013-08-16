from .default import *

#
#  Django Production
#..........................

ALLOWED_HOSTS = tuple(envini.getstrings('host'))
SCREAMSHOT_CONFIG['CAPTURE_ALLOWED_IPS'] += ALLOWED_HOSTS

USE_X_FORWARDED_HOST = True

MAPENTITY_CONFIG['CONVERSION_SERVER'] = '%s/convert' % ROOT_URL

COMPRESSOR_ENABLED = True

INSTALLED_APPS += (
    'gunicorn',
)

CACHES['default']['BACKEND'] = 'django.core.cache.backends.memcached.MemcachedCache'
CACHES['default']['LOCATION'] = '127.0.0.1:11211'

#
#  Email settings
#..........................

ADMINS = (
    ('Admin %s' % TITLE, envini.get('mailadmin')),
)
MANAGERS = ADMINS
EMAIL_SUBJECT_PREFIX = '[%s] ' % TITLE
DEFAULT_FROM_EMAIL = envini.get('mailfrom', envini.get('mailadmin'))
SERVER_EMAIL = DEFAULT_FROM_EMAIL
EMAIL_HOST = envini.get('mailhost')
EMAIL_HOST_USER = envini.get('mailhost')
EMAIL_HOST_PASSWORD = envini.get('mailpassword')
EMAIL_HOST_PORT = envini.get('mailport', 25)
EMAIL_USE_TLS = envini.get('mailtls', False)

#
#  External authent
#..........................

AUTHENT_DATABASE = envini.get('authent_dbname', 'authentdb')
AUTHENT_TABLENAME = envini.get('authent_tablename', None)
if AUTHENT_TABLENAME:
    AUTHENTICATION_BACKENDS = ('geotrek.authent.backend.DatabaseBackend',)

DATABASES[AUTHENT_DATABASE] = {}
DATABASES[AUTHENT_DATABASE]['ENGINE'] = 'django.db.backends.%s' % envini.get('authent_engine', 'postgresql_psycopg2')
DATABASES[AUTHENT_DATABASE]['NAME'] = AUTHENT_DATABASE
DATABASES[AUTHENT_DATABASE]['USER'] = envini.get('authent_dbuser')
DATABASES[AUTHENT_DATABASE]['PASSWORD'] = envini.get('authent_dbpassword')
DATABASES[AUTHENT_DATABASE]['HOST'] = envini.get('authent_dbhost')
DATABASES[AUTHENT_DATABASE]['PORT'] = envini.get('authent_dbport', 5432)
