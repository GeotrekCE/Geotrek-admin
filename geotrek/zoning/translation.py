from modeltranslation.translator import TranslationOptions, translator

from geotrek.zoning import models


class VigilanceAreaTO(TranslationOptions):
    fields = (
        "name",
        "description",
        "practical_info",
    )


class VigilanceAreaTypeTO(TranslationOptions):
    fields = ("name",)


class VigilanceLevelTO(TranslationOptions):
    fields = ("name",)


translator.register(models.VigilanceAreaType, VigilanceAreaTypeTO)
translator.register(models.VigilanceArea, VigilanceAreaTO)
translator.register(models.VigilanceLevel, VigilanceLevelTO)
