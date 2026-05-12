from django.conf import settings
from modeltranslation.translator import TranslationOptions, translator

from geotrek.trekking import models as trekking_models

# Trek app


class TrekTO(TranslationOptions):
    fields = (
        "name",
        "departure",
        "arrival",
        "description_teaser",
        "description",
        "ambiance",
        "access",
        "accessibility_infrastructure",
        "advice",
        "gear",
        "accessibility_signage",
        "accessibility_slope",
        "accessibility_covering",
        "accessibility_exposure",
        "accessibility_width",
        "accessibility_advice",
        "advised_parking",
        "public_transport",
        "ratings_description",
    ) + (("published",) if settings.PUBLISHED_BY_LANG else tuple())
    fallback_undefined = {"published": None}


class POITO(TranslationOptions):
    fields = ("name", "description") + (
        ("published",) if settings.PUBLISHED_BY_LANG else tuple()
    )
    fallback_undefined = {"published": None}


class POITypeTO(TranslationOptions):
    fields = ("label",)


class TrekNetworkTO(TranslationOptions):
    fields = ("network",)


class PracticeTO(TranslationOptions):
    fields = ("name",)


class AccessibilityTO(TranslationOptions):
    fields = ("name",)


class AccessibilityLevelTO(TranslationOptions):
    fields = ("name",)


class RouteTO(TranslationOptions):
    fields = ("route",)


class DifficultyLevelTO(TranslationOptions):
    fields = ("difficulty",)


class WebLinkTO(TranslationOptions):
    fields = ("name",)


class WebLinkCategoryTO(TranslationOptions):
    fields = ("label",)


class RatingScaleTO(TranslationOptions):
    fields = ("name",)


class RatingTO(TranslationOptions):
    fields = ("name", "description")


class ServiceTypeTO(TranslationOptions):
    fields = ("name",)


# Register previously defined translation options
trek_translation_to_register = [
    (trekking_models.Trek, TrekTO),
    (trekking_models.POI, POITO),
    (trekking_models.POIType, POITypeTO),
    (trekking_models.TrekNetwork, TrekNetworkTO),
    (trekking_models.Practice, PracticeTO),
    (trekking_models.Accessibility, AccessibilityTO),
    (trekking_models.AccessibilityLevel, AccessibilityLevelTO),
    (trekking_models.Route, RouteTO),
    (trekking_models.DifficultyLevel, DifficultyLevelTO),
    (trekking_models.WebLink, WebLinkTO),
    (trekking_models.WebLinkCategory, WebLinkCategoryTO),
    (trekking_models.ServiceType, ServiceTypeTO),
    (trekking_models.Rating, RatingTO),
    (trekking_models.RatingScale, RatingScaleTO),
]

for model, model_to in trek_translation_to_register:
    translator.register(model, model_to)
