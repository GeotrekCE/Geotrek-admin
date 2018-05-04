from .base import *
from .base import _

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
    ('en', _('English')),
    ('es', _('Spanish')),
    ('fr', _('French')),
    ('it', _('Italian')),
)

MAILALERTSUBJECT = "Acknowledgment of feedback email"

ALLOWED_HOSTS = [
    'localhost',
]


class DisableMigrations(object):
    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return None


MIGRATION_MODULES = DisableMigrations()

SECRET_KEY = "Ceci n'est pas du tout secret mais c'est juste pour les tests"

DATABASES['default']['TEST'] = {
    'SERIALIZE': False,
}
