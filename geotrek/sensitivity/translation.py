from modeltranslation.translator import translator, TranslationOptions
from geotrek.sensitivity.models import SportPractice, Species


# Sensitivity app

class SportPracticeTO(TranslationOptions):
    fields = ('name', )


class SpeciesTO(TranslationOptions):
    fields = ('name', )


translator.register(SportPractice, SportPracticeTO)
translator.register(Species, SpeciesTO)
