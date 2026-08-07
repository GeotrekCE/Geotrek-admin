from django.conf import settings
from mapentity.registry import MapEntityOptions


class SignageEntityOptions(MapEntityOptions):
    menu = settings.SIGNAGE_MODEL_ENABLED
    layer = settings.SIGNAGE_MODEL_ENABLED


class BladeEntityOptions(MapEntityOptions):
    menu = False
    layer = False
