#
#  Django Tests
# ..........................
from .base import *  # noqa
from tempfile import TemporaryDirectory
import os
import django.test.runner
from django.conf import settings
import tempfile

TEST = True

ALLOWED_HOSTS = ['localhost']

CELERY_ALWAYS_EAGER = True

INSTALLED_APPS += (
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


class DisableMigrations:
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

import warnings
warnings.filterwarnings("ignore")

LOGGING['loggers']['']['handlers'] = ('log_file', )
LOGGING['handlers']['log_file']['level'] = 'INFO'
LOGGING['handlers']['log_file']['filename'] = os.path.join(TMP_DIR, 'geotrek.log')

# Silence all console / stream handlers to avoid cluttering test outputs
for handler in LOGGING.get('handlers', {}).values():
    if handler.get('class') == 'logging.StreamHandler':
        handler['level'] = 'CRITICAL'
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

# --- Monkey-patch Django's parallel test worker initialization ---
_original_init_worker = django.test.runner._init_worker

def _patched_init_worker(*args, **kwargs):
    # Create isolated directories for this specific worker process
    result = _original_init_worker(*args, **kwargs)
    worker_tmp = tempfile.mkdtemp(prefix=f"geotrek_worker_{os.getpid()}_", dir=TMP_DIR)
    
    settings.MEDIA_ROOT = os.path.join(worker_tmp, 'media')
    settings.MAP_PATH = os.path.join(settings.MEDIA_ROOT, 'maps')
    os.makedirs(settings.MAP_PATH, exist_ok=True)
    
    settings.SYNC_MOBILE_ROOT = os.path.join(worker_tmp, 'sync_mobile')
    os.makedirs(settings.SYNC_MOBILE_ROOT, exist_ok=True)
    
    settings.MOBILE_TILES_PATH = os.path.join(worker_tmp, 'tiles')
    os.makedirs(settings.MOBILE_TILES_PATH, exist_ok=True)
    
    settings.DATA_TEMP_DIR = os.path.join(worker_tmp, 'data')
    os.makedirs(settings.DATA_TEMP_DIR, exist_ok=True)
    
    return result

django.test.runner._init_worker = _patched_init_worker

