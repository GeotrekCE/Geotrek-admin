from django.conf import settings
from geotrek.outdoor.models import Site, Practice, SiteType, RatingScale, Rating, Sector, Course
from modeltranslation.translator import translator, TranslationOptions


class SiteTO(TranslationOptions):
    fields = ('name', 'description', 'description_teaser', 'ambiance', 'advice', 'period') + (
        ('published',) if settings.PUBLISHED_BY_LANG else tuple())
    fallback_undefined = {'published': None}


class SectorTO(TranslationOptions):
    fields = ('name', )


class PracticeTO(TranslationOptions):
    fields = ('name', )


class SiteTypeTO(TranslationOptions):
    fields = ('name', )


class RatingScaleTO(TranslationOptions):
    fields = ('name', )


class RatingTO(TranslationOptions):
    fields = ('name', 'description')


class CourseTO(TranslationOptions):
    fields = ('name', 'description', 'advice') + (
        ('published',) if settings.PUBLISHED_BY_LANG else tuple())
    fallback_undefined = {'published': None}


translator.register(Site, SiteTO)
translator.register(Sector, SectorTO)
translator.register(Practice, PracticeTO)
translator.register(SiteType, SiteTypeTO)
translator.register(RatingScale, RatingScaleTO)
translator.register(Rating, RatingTO)
translator.register(Course, CourseTO)
