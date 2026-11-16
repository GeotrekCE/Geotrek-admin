from django.conf import settings
from mapentity.registry import MapEntityOptions


class SensitiveAreaEntityOptions(MapEntityOptions):
    menu = settings.SENSITIVE_AREA_MODEL_ENABLED
    layer = settings.SENSITIVE_AREA_MODEL_ENABLED
