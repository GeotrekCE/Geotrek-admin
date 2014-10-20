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
