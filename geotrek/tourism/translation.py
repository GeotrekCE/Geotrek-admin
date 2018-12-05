from django.conf import settings

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
    fields = ('name', 'description_teaser', 'description', 'practical_info'
              ) + (('published',) if settings.PUBLISHED_BY_LANG else tuple())
    fallback_undefined = {'published': None}


translator.register(tourism_models.TouristicContent, TouristicContentTO)


class TouristicContentCategoryTO(TranslationOptions):
    fields = ('label', 'type1_label', 'type2_label')


translator.register(tourism_models.TouristicContentCategory,
                    TouristicContentCategoryTO)


class TouristicContentTypeTO(TranslationOptions):
    fields = ('label',)


translator.register(tourism_models.TouristicContentType,
                    TouristicContentTypeTO)
translator.register(tourism_models.TouristicContentType1,
                    TouristicContentTypeTO)
translator.register(tourism_models.TouristicContentType2,
                    TouristicContentTypeTO)


class TouristicEventTypeTO(TranslationOptions):
    fields = ('type',)


translator.register(tourism_models.TouristicEventType, TouristicEventTypeTO)


class TouristicEventTO(TranslationOptions):
    fields = ('name', 'description_teaser', 'description', 'meeting_point',
              'accessibility', 'booking', 'practical_info', 'target_audience',
              ) + (('published',) if settings.PUBLISHED_BY_LANG else tuple())
    fallback_undefined = {'published': None}


translator.register(tourism_models.TouristicEvent, TouristicEventTO)
