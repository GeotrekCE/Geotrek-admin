from modeltranslation.translator import translator, TranslationOptions
from geotrek.sensitivity.models import SportPractice, Species, SensitiveArea


# Sensitivity app

class SportPracticeTO(TranslationOptions):
    fields = ('name', )


class SpeciesTO(TranslationOptions):
    fields = ('name', 'url')


class SensitiveAreaTO(TranslationOptions):
    fields = ('name', 'description', )


translator.register(SportPractice, SportPracticeTO)
translator.register(Species, SpeciesTO)
translator.register(SensitiveArea, SensitiveAreaTO)
