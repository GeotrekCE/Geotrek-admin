from django.conf import settings
from modeltranslation.translator import TranslationOptions, translator

from geotrek.signage.models import Signage


class SignageTO(TranslationOptions):
    fields = ("description", "name") + (
        ("published",) if settings.PUBLISHED_BY_LANG else tuple()
    )
    fallback_undefined = {"published": None}


translator.register(Signage, SignageTO)
