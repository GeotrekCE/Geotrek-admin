from modeltranslation.translator import translator, TranslationOptions

from geotrek.tourism import models as tourism_models


class DataSourceTO(TranslationOptions):
    fields = ('title',)

translator.register(tourism_models.DataSource, DataSourceTO)


class InformationDeskTO(TranslationOptions):
    fields = ('name', 'description')

translator.register(tourism_models.InformationDesk, InformationDeskTO)


class InformationDeskTypeTO(TranslationOptions):
    fields = ('label',)

translator.register(tourism_models.InformationDeskType, InformationDeskTypeTO)


class TouristicContentTO(TranslationOptions):
    fields = ('name',)

translator.register(tourism_models.TouristicContent, TouristicContentTO)


class TouristicContentCategoryTO(TranslationOptions):
    fields = ('label',)


translator.register(tourism_models.TouristicContentCategory,
                    TouristicContentCategoryTO)
