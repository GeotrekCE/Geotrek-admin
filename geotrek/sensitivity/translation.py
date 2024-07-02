from modeltranslation.translator import translator, TranslationOptions
from geotrek.sensitivity.models import Rule, SportPractice, Species, SensitiveArea


# Sensitivity app
class RuleTO(TranslationOptions):
    all_fields = ('name', 'description', )


class SportPracticeTO(TranslationOptions):
    all_fields = ('name', )


class SpeciesTO(TranslationOptions):
    all_fields = ('name', 'url', )


class SensitiveAreaTO(TranslationOptions):
    all_fields = ('description', )


translator.register(Rule, RuleTO)
translator.register(SportPractice, SportPracticeTO)
translator.register(Species, SpeciesTO)
translator.register(SensitiveArea, SensitiveAreaTO)
