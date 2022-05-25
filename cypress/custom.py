SURICATE_WORKFLOW_ENABLED = True
TEST = True
LANGUAGE_CODE = os.getenv('LANGUAGE_CODE', 'en')

MODELTRANSLATION_LANGUAGES = tuple(os.getenv('LANGUAGES', 'en fr').split(' '))
