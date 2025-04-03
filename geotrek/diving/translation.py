from django.conf import settings
from modeltranslation.translator import TranslationOptions, translator

from geotrek.diving import models as diving_models

# Trek app


class DiveTO(TranslationOptions):
    fields = (
        "name",
        "departure",
        "description_teaser",
        "facilities",
        "description",
        "disabled_sport",
        "advice",
    ) + (("published",) if settings.PUBLISHED_BY_LANG else tuple())
    fallback_undefined = {"published": None}


class PracticeTO(TranslationOptions):
    fields = ("name",)


class DifficultyTO(TranslationOptions):
    fields = ("name",)


class LevelTO(TranslationOptions):
    fields = ("name", "description")


# Register previously defined translation options
translation_to_register = [
    (diving_models.Dive, DiveTO),
    (diving_models.Practice, PracticeTO),
    (diving_models.Difficulty, DifficultyTO),
    (diving_models.Level, LevelTO),
]

for model, model_to in translation_to_register:
    translator.register(model, model_to)
