from django.conf import settings
from modeltranslation.translator import TranslationOptions, translator

from geotrek.infrastructure.models import Infrastructure


class InfrastructureTO(TranslationOptions):
    fields = ("accessibility", "description", "name") + (
        ("published",) if settings.PUBLISHED_BY_LANG else tuple()
    )
    fallback_undefined = {"published": None}


translator.register(Infrastructure, InfrastructureTO)
