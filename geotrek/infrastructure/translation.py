from django.conf import settings
from geotrek.infrastructure.models import Infrastructure
from modeltranslation.translator import translator, TranslationOptions


class InfrastructureTO(TranslationOptions):
    all_fields = ('accessibility', 'description', 'name') + (
        ('published',) if settings.PUBLISHED_BY_LANG else tuple())
    fallback_undefined = {'published': None}


translator.register(Infrastructure, InfrastructureTO)
