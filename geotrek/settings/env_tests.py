#
#  Django Tests
# ..........................

TEST = True

CELERY_ALWAYS_EAGER = True

TEST_EXCLUDE = ('django',)

INSTALLED_APPS += (
    'geotrek.diving',
    'geotrek.sensitivity',
)

LOGGING['handlers']['console']['level'] = 'CRITICAL'

LANGUAGE_CODE = 'en'
MODELTRANSLATION_DEFAULT_LANGUAGE = 'en'
MODELTRANSLATION_LANGUAGES = ('en', 'es', 'fr', 'it')

LAND_BBOX_AREAS_ENABLED = True


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

TEST_RUNNER = 'geotrek.test_runner.TestRunner'
