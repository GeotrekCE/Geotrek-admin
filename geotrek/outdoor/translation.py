from django.conf import settings
from modeltranslation.translator import TranslationOptions, translator

from geotrek.outdoor.models import (
    Course,
    CourseType,
    Practice,
    Rating,
    RatingScale,
    Sector,
    Site,
    SiteType,
)


class SiteTO(TranslationOptions):
    fields = (
        "name",
        "description",
        "description_teaser",
        "ambiance",
        "accessibility",
        "advice",
        "period",
    ) + (("published",) if settings.PUBLISHED_BY_LANG else tuple())
    fallback_undefined = {"published": None}


class SectorTO(TranslationOptions):
    fields = ("name",)


class PracticeTO(TranslationOptions):
    fields = ("name",)


class SiteTypeTO(TranslationOptions):
    fields = ("name",)


class CourseTypeTO(TranslationOptions):
    fields = ("name",)


class RatingScaleTO(TranslationOptions):
    fields = ("name",)


class RatingTO(TranslationOptions):
    fields = ("name", "description")


class CourseTO(TranslationOptions):
    fields = (
        "name",
        "description",
        "equipment",
        "accessibility",
        "advice",
        "gear",
        "ratings_description",
    ) + (("published",) if settings.PUBLISHED_BY_LANG else tuple())
    fallback_undefined = {"published": None}


translator.register(Site, SiteTO)
translator.register(Sector, SectorTO)
translator.register(Practice, PracticeTO)
translator.register(SiteType, SiteTypeTO)
translator.register(CourseType, CourseTypeTO)
translator.register(RatingScale, RatingScaleTO)
translator.register(Rating, RatingTO)
translator.register(Course, CourseTO)
