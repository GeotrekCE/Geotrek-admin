from django.conf import settings
from mapentity.registry import MapEntityOptions


class VigilanceAreaEntityOptions(MapEntityOptions):
    menu = settings.VIGILANCE_AREA_MODEL_ENABLED
    layer = settings.VIGILANCE_AREA_MODEL_ENABLED
