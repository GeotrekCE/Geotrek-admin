from .default import *

#
# Django Production
# ..........................

ALLOWED_HOSTS = tuple('*')

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
# Optimizations
# ..........................

DATABASES['default']['CONN_MAX_AGE'] = 600

# Template caching is not compatible with MAPENTITY_CONFIG['MAPENTITY_WEASYPRINT'] = False
# TEMPLATES[1]['OPTIONS']['loaders'] = (
#     ('django.template.loaders.cached.Loader',
#      TEMPLATES[1]['OPTIONS']['loaders']),
# )

# SESSION_ENGINE = 'django.contrib.sessions.backends.cache'

#
# Email settings
# ..........................

admins = "admin@yourdomain.tld"
ADMINS = tuple([('Admin %s' % TITLE, admin) for admin in admins])

managers = "manager1@yourdomain.tld", "manager2@yourdomain.tld"
MANAGERS = tuple([('Manager %s' % TITLE, manager) for manager in managers])

DEFAULT_FROM_EMAIL ="admin@yourdomain.tld"
SERVER_EMAIL = DEFAULT_FROM_EMAIL
EMAIL_HOST = ""
EMAIL_HOST_USER = ""
EMAIL_HOST_PASSWORD = ""
EMAIL_HOST_PORT = 25
EMAIL_USE_TLS = False
EMAIL_USE_SSL = False

#
# External authent
# ..........................

AUTHENT_DATABASE = 'authentdb'
AUTHENT_TABLENAME = None
if AUTHENT_TABLENAME:
    AUTHENTICATION_BACKENDS = ('geotrek.authent.backend.DatabaseBackend',)

DATABASES[AUTHENT_DATABASE] = {}
DATABASES[AUTHENT_DATABASE]['ENGINE'] = 'django.db.backends.postgresql_psycopg2'
DATABASES[AUTHENT_DATABASE]['NAME'] = AUTHENT_DATABASE
DATABASES[AUTHENT_DATABASE]['USER'] = None
DATABASES[AUTHENT_DATABASE]['PASSWORD'] = None
DATABASES[AUTHENT_DATABASE]['HOST'] = None
DATABASES[AUTHENT_DATABASE]['PORT'] = 5432
