from django.conf import settings
from geotrek.outdoor.models import Site, Practice, SiteType, RatingScale, Rating
from modeltranslation.translator import translator, TranslationOptions


class SiteTO(TranslationOptions):
    fields = ('name', 'description', 'description_teaser', 'ambiance', 'advice', 'period') + (
        ('published',) if settings.PUBLISHED_BY_LANG else tuple())
    fallback_undefined = {'published': None}


class PracticeTO(TranslationOptions):
    fields = ('name', )


class SiteTypeTO(TranslationOptions):
    fields = ('name', )


class RatingScaleTO(TranslationOptions):
    fields = ('name', )


class RatingTO(TranslationOptions):
    fields = ('name', 'description')


translator.register(Site, SiteTO)
translator.register(Practice, PracticeTO)
translator.register(SiteType, SiteTypeTO)
translator.register(RatingScale, RatingScaleTO)
translator.register(Rating, RatingTO)
