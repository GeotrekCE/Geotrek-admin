from django.conf import settings
from geotrek.signage.models import Signage
from modeltranslation.translator import translator, TranslationOptions


class SignageTO(TranslationOptions):
    all_fields = ('description', 'name') + (
        ('published',) if settings.PUBLISHED_BY_LANG else tuple())
    fallback_undefined = {'published': None}


translator.register(Signage, SignageTO)
