from django.conf import settings
from mapentity.registry import MapEntityOptions


class InterventionEntityOptions(MapEntityOptions):
    menu = settings.INTERVENTION_MODEL_ENABLED
    layer = settings.INTERVENTION_MODEL_ENABLED


class ProjectEntityOptions(MapEntityOptions):
    menu = settings.PROJECT_MODEL_ENABLED
    layer = settings.PROJECT_MODEL_ENABLED
