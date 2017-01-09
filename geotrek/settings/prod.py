from .default import *

#
# Django Production
# ..........................

ALLOWED_HOSTS = tuple(envini.getstrings('host', default='*'))

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
                                  'filename': os.path.join(DEPLOY_ROOT, 'var', 'log', 'geotrek.log')}
LOGGING['loggers']['geotrek']['handlers'].append('logfile')
LOGGING['loggers']['mapentity']['handlers'].append('logfile')

#
# Optimitizations
# ..........................

DATABASES['default']['CONN_MAX_AGE'] = 600
TEMPLATES[1]['OPTIONS']['loaders'] = (
    ('django.template.loaders.cached.Loader',
     TEMPLATES[1]['OPTIONS']['loaders']),
)
# SESSION_ENGINE = 'django.contrib.sessions.backends.cache'

#
# Email settings
# ..........................

admins = envini.getstrings('mailadmins')
ADMINS = tuple([('Admin %s' % TITLE, admin) for admin in admins])

managers = envini.getstrings('mailmanagers')
MANAGERS = tuple([('Manager %s' % TITLE, manager) for manager in managers])

DEFAULT_FROM_EMAIL = envini.get('mailfrom', admins[0])
SERVER_EMAIL = DEFAULT_FROM_EMAIL
EMAIL_HOST = envini.get('mailhost')
EMAIL_HOST_USER = envini.get('mailhost')
EMAIL_HOST_PASSWORD = envini.get('mailpassword')
EMAIL_HOST_PORT = envini.get('mailport', 25)
EMAIL_USE_TLS = envini.getbool('mailtls', 'False')

#
# External authent
# ..........................

AUTHENT_DATABASE = envini.get('authent_dbname', 'authentdb')
AUTHENT_TABLENAME = envini.get('authent_tablename', None)
if AUTHENT_TABLENAME:
    AUTHENTICATION_BACKENDS = ('geotrek.authent.backend.DatabaseBackend',)

DATABASES[AUTHENT_DATABASE] = {}
DATABASES[AUTHENT_DATABASE]['ENGINE'] = 'django.db.backends.%s' % envini.get('authent_engine', 'postgresql_psycopg2')
DATABASES[AUTHENT_DATABASE]['NAME'] = AUTHENT_DATABASE
DATABASES[AUTHENT_DATABASE]['USER'] = envini.get('authent_dbuser', None)
DATABASES[AUTHENT_DATABASE]['PASSWORD'] = envini.get('authent_dbpassword', None)
DATABASES[AUTHENT_DATABASE]['HOST'] = envini.get('authent_dbhost', None)
DATABASES[AUTHENT_DATABASE]['PORT'] = envini.get('authent_dbport', 5432)
