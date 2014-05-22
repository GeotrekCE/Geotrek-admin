from modeltranslation.translator import translator, TranslationOptions

from geotrek.tourism.models import DataSource


class DataSourceTO(TranslationOptions):
    fields = ('title',)

translator.register(DataSource, DataSourceTO)
