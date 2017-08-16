from modeltranslation.translator import translator, TranslationOptions
from geotrek.sensitivity.models import SportPractice, Species, SensitiveArea
from django.conf import settings


# Sensitivity app

class SportPracticeTO(TranslationOptions):
    fields = ('name', )


class SpeciesTO(TranslationOptions):
    fields = ('name', )


class SensitiveAreaTO(TranslationOptions):
    fields = ('published', ) if settings.PUBLISHED_BY_LANG else ()
    fallback_undefined = {'published': None}


translator.register(SportPractice, SportPracticeTO)
translator.register(Species, SpeciesTO)
translator.register(SensitiveArea, SensitiveAreaTO)
