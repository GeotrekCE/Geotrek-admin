from .base import * #noqa

#
#  Django Tests
# ..........................

TEST = True

TEST_EXCLUDE = ('django',)

INSTALLED_APPS += ('geotrek.sensitivity',)

LOGGING['handlers']['console']['level'] = 'CRITICAL'

LANGUAGE_CODE = 'en'
MODELTRANSLATION_DEFAULT_LANGUAGE = 'en'
MODELTRANSLATION_LANGUAGES = ('en', 'es', 'fr', 'it')
MAPENTITY_CONFIG['TRANSLATED_LANGUAGES'] = (
    ('en', 'English'),
    ('es', 'Spanish'),
    ('fr', 'French'),
    ('it', 'Italian'),
)

MAILALERTSUBJECT = "Acknowledgment of feedback email"

ALLOWED_HOSTS = [
    'localhost',
]


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
