from .default import *

#
#  Django Tests
# ..........................

TEST = True

TEST_EXCLUDE = ('django',)

INSTALLED_APPS += (
    'geotrek.diving',
    'geotrek.sensitivity',
)

LOGGING['handlers']['console']['level'] = 'CRITICAL'

LANGUAGE_CODE = 'en'
MODELTRANSLATION_DEFAULT_LANGUAGE = 'en'
MODELTRANSLATION_LANGUAGES = ('en', 'es', 'fr', 'it')
MAPENTITY_CONFIG['TRANSLATED_LANGUAGES'] = (
    ('en', gettext_noop('English')),
    ('es', gettext_noop('Spanish')),
    ('fr', gettext_noop('French')),
    ('it', gettext_noop('Italian')),
)

ALLOWED_HOSTS = [
    'localhost',
]


class DisableMigrations(object):
    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return None


MIGRATION_MODULES = DisableMigrations()
