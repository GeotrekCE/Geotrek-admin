#
#  Django Tests
# ..........................
from .base import *  # noqa
import shutil
from tempfile import TemporaryDirectory
import os

TEST = True

ALLOWED_HOSTS = ['localhost']

CELERY_ALWAYS_EAGER = True

ALLOWED_HOSTS = ['localhost']

INSTALLED_APPS += (
    'geotrek.diving',
    'geotrek.sensitivity',
    'geotrek.outdoor',
    'drf_yasg',
)

LANGUAGE_CODE = 'en'
MODELTRANSLATION_DEFAULT_LANGUAGE = 'en'
MODELTRANSLATION_LANGUAGES = ('en', 'es', 'fr', 'it')

LAND_BBOX_AREAS_ENABLED = True

TIME_ZONE = "UTC"

CACHES['default'] = {
    'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    'LOCATION': 'default',
}
CACHES['fat'] = {
    'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    'LOCATION': 'fat',
}
CACHES['api_v2'] = {
    'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    'LOCATION': 'api_v2',
}


class DisableMigrations():
    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return None


MIGRATION_MODULES = DisableMigrations()

ADMINS = (
    ('test', 'test@test.com'),
)

MANAGERS = ADMINS

# recreate TMP_DIR for tests, and it as base dir for all files
TMP_DIR = TemporaryDirectory().name
os.makedirs(TMP_DIR)
SESSION_FILE_PATH = os.path.join(TMP_DIR, 'sessions')
os.makedirs(SESSION_FILE_PATH)

LOGGING['loggers']['']['handlers'] = ('log_file', )
LOGGING['handlers']['log_file']['level'] = 'INFO'
LOGGING['handlers']['log_file']['filename'] = os.path.join(TMP_DIR, 'geotrek.log')
MEDIA_ROOT = TemporaryDirectory(dir=TMP_DIR).name  # media files
MAP_PATH = os.path.join(MEDIA_ROOT, 'maps')  # map files
os.makedirs(MAP_PATH)
SYNC_MOBILE_ROOT = TemporaryDirectory(dir=TMP_DIR).name  # sync mobile root path
MOBILE_TILES_PATH = TemporaryDirectory(dir=TMP_DIR).name  # sync mobile tile path
DATA_TEMP_DIR = TemporaryDirectory(dir=TMP_DIR).name  # data temp dir use by django-large-image
REDIS_URL = f"redis://{os.getenv('REDIS_HOST', 'localhost')}:{os.getenv('REDIS_PORT', '6379')}/1"  # celery broker url
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]
