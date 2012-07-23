from modeltranslation.translator import translator, TranslationOptions

from caminae.maintenance import models as maintenance_models
from caminae.land import models as land_models
from caminae.trekking import models as trekking_models


## Maintenance app ##

class InterventionStatusTO(TranslationOptions):
    fields = ('status',)


class InterventionTypologyTO(TranslationOptions):
    fields = ('typology', )


class InterventionDisorderTO(TranslationOptions):
    fields = ('disorder', )


translator.register(maintenance_models.InterventionStatus, InterventionStatusTO)
translator.register(maintenance_models.InterventionTypology, InterventionTypologyTO)
translator.register(maintenance_models.InterventionDisorder, InterventionDisorderTO)


# Land app

class PhysicalTypeTO(TranslationOptions):
    fields = ('name', )

translator.register(land_models.PhysicalType, PhysicalTypeTO)


# Trek app

class TrekTO(TranslationOptions):
    fields = ('name', 'departure', 'arrival', 'description_teaser',
        'description', 'ambiance', 'handicapped_infrastructure', 'advice', )


class TrekNetworkTO(TranslationOptions):
    fields = ('network', )


class UsageTO(TranslationOptions):
    fields = ('usage', )


class RouteTO(TranslationOptions):
    fields = ('route', )


class DifficultyLevelTO(TranslationOptions):
    fields = ('difficulty', )


class DestinationTO(TranslationOptions):
    fields = ('destination', )


class WebLinkTO(TranslationOptions):
    fields = ('name', )


# Register previously defined translation options
trek_translation_to_register = [
    (trekking_models.Trek, TrekTO),
    (trekking_models.TrekNetwork, TrekNetworkTO),
    (trekking_models.Usage, UsageTO),
    (trekking_models.Route, RouteTO),
    (trekking_models.DifficultyLevel, DifficultyLevelTO),
    (trekking_models.Destination, DestinationTO),
    (trekking_models.WebLink, WebLinkTO),
]

for model, model_to in trek_translation_to_register:
    translator.register(model, model_to)

