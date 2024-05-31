from django.conf import settings

from modeltranslation.translator import translator, TranslationOptions

from geotrek.trekking import models as trekking_models


# Trek app

class TrekTO(TranslationOptions):
    all_fields = (
        'name', 'departure', 'arrival', 'description_teaser', 'description', 'ambiance', 'access',
        'accessibility_infrastructure', 'advice', 'gear', 'accessibility_signage', 'accessibility_slope',
        'accessibility_covering', 'accessibility_exposure', 'accessibility_width',
        'accessibility_advice', 'advised_parking', 'public_transport', 'ratings_description'
    ) + (('published',) if settings.PUBLISHED_BY_LANG else tuple())
    fallback_undefined = {'published': None}


class POITO(TranslationOptions):
    all_fields = ('name', 'description') + (
        ('published',) if settings.PUBLISHED_BY_LANG else tuple()
    )
    fallback_undefined = {'published': None}


class POITypeTO(TranslationOptions):
    all_fields = ('label', )


class TrekNetworkTO(TranslationOptions):
    all_fields = ('network', )


class PracticeTO(TranslationOptions):
    all_fields = ('name', )


class AccessibilityTO(TranslationOptions):
    all_fields = ('name', )


class AccessibilityLevelTO(TranslationOptions):
    all_fields = ('name', )


class RouteTO(TranslationOptions):
    all_fields = ('route', )


class DifficultyLevelTO(TranslationOptions):
    all_fields = ('difficulty', )


class WebLinkTO(TranslationOptions):
    all_fields = ('name', )


class WebLinkCategoryTO(TranslationOptions):
    all_fields = ('label', )


class RatingScaleTO(TranslationOptions):
    all_fields = ('name', )


class RatingTO(TranslationOptions):
    all_fields = ('name', 'description')


class ServiceTypeTO(TranslationOptions):
    all_fields = ('name', )


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
    (trekking_models.RatingScale, RatingScaleTO)
]

for model, model_to in trek_translation_to_register:
    translator.register(model, model_to)
