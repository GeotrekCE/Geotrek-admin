from django.conf import settings
from mapentity.registry import MapEntityOptions


class InfrastructureOptions(MapEntityOptions):
    menu = settings.INFRASTRUCTURE_MODEL_ENABLED
    layer = settings.INFRASTRUCTURE_MODEL_ENABLED
