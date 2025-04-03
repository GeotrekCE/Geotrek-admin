from modeltranslation.translator import TranslationOptions, translator

from geotrek.sensitivity.models import Rule, SensitiveArea, Species, SportPractice


# Sensitivity app
class RuleTO(TranslationOptions):
    fields = (
        "name",
        "description",
    )


class SportPracticeTO(TranslationOptions):
    fields = ("name",)


class SpeciesTO(TranslationOptions):
    fields = (
        "name",
        "url",
    )


class SensitiveAreaTO(TranslationOptions):
    fields = ("description",)


translator.register(Rule, RuleTO)
translator.register(SportPractice, SportPracticeTO)
translator.register(Species, SpeciesTO)
translator.register(SensitiveArea, SensitiveAreaTO)
