from django.conf import settings
from mapentity.registry import MapEntityOptions


class ReportOptions(MapEntityOptions):
    menu = settings.REPORT_MODEL_ENABLED
    layer = settings.REPORT_MODEL_ENABLED
