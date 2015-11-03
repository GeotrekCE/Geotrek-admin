from .default import *  # NOQA

#
#  Django Tests
# ..........................

TEST = True

TEST_EXCLUDE = ('django',)

LOGGING['handlers']['console']['level'] = 'CRITICAL'

LANGUAGE_CODE = 'en'

SOUTH_TESTS_MIGRATE = False

MAPENTITY_CONFIG['MAPENTITY_WEASYPRINT'] = False

MAILALERTSUBJECT = "Acknowledgment of feedback email"

DATABASES['default']['NAME'] = "geotrekdb"
DATABASES['default']['USER'] = "postgres"
DATABASES['default']['PASSWORD'] = "postgres"
DATABASES['default']['HOST'] = "10.0.3.92"
DATABASES['default']['PORT'] = 5432
