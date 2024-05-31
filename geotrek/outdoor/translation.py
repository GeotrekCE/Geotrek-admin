from django.conf import settings
from geotrek.outdoor.models import CourseType, Site, Practice, SiteType, RatingScale, Rating, Sector, Course
from modeltranslation.translator import translator, TranslationOptions


class SiteTO(TranslationOptions):
    all_fields = ('name', 'description', 'description_teaser', 'ambiance', 'accessibility', 'advice', 'period') + (
        ('published',) if settings.PUBLISHED_BY_LANG else tuple())
    fallback_undefined = {'published': None}


class SectorTO(TranslationOptions):
    all_fields = ('name', )


class PracticeTO(TranslationOptions):
    all_fields = ('name', )


class SiteTypeTO(TranslationOptions):
    all_fields = ('name', )


class CourseTypeTO(TranslationOptions):
    all_fields = ('name', )


class RatingScaleTO(TranslationOptions):
    all_fields = ('name', )


class RatingTO(TranslationOptions):
    all_fields = ('name', 'description')


class CourseTO(TranslationOptions):
    all_fields = ('name', 'description', 'equipment', 'accessibility', 'advice', 'gear', 'ratings_description') + (
        ('published',) if settings.PUBLISHED_BY_LANG else tuple())
    fallback_undefined = {'published': None}


translator.register(Site, SiteTO)
translator.register(Sector, SectorTO)
translator.register(Practice, PracticeTO)
translator.register(SiteType, SiteTypeTO)
translator.register(CourseType, CourseTypeTO)
translator.register(RatingScale, RatingScaleTO)
translator.register(Rating, RatingTO)
translator.register(Course, CourseTO)
