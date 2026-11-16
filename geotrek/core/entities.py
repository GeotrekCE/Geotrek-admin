from django.conf import settings

from geotrek.altimetry.mixins import AltimetryEntityOptions


class PathEntityOptions(AltimetryEntityOptions):
    menu = settings.PATH_MODEL_ENABLED
    layer = settings.PATH_MODEL_ENABLED


class TrailEntityOptions(AltimetryEntityOptions):
    menu = settings.TRAIL_MODEL_ENABLED
    layer = settings.TRAIL_MODEL_ENABLED
