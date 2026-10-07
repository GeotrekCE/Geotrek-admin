from django.conf import settings
from mapentity.registry import MapEntityOptions

from geotrek.altimetry.mixins import AltimetryEntityOptions
from geotrek.common.mixins.entity_options import PublishableEntityOptions
from geotrek.trekking.views import (
    TrekDocumentBookletPublic,
    TrekDocumentPublic,
    TrekMarkupPublic,
)


class TrekEntityOptions(AltimetryEntityOptions, PublishableEntityOptions):
    """
    Add more urls using mixins:
    - altimetry views (profile, dem etc.)
    - public documents views
    We override trek public view to add more context variables and
    preprocess attributes.
    """

    document_public_view = TrekDocumentPublic
    document_public_booklet_view = TrekDocumentBookletPublic
    markup_public_view = TrekMarkupPublic
    menu = settings.TREKKING_MODEL_ENABLED
    layer = settings.TREKKING_MODEL_ENABLED


class POIEntityOptions(PublishableEntityOptions):
    menu = settings.POI_MODEL_ENABLED
    layer = settings.POI_MODEL_ENABLED


class ServiceEntityOptions(MapEntityOptions):
    menu = settings.SERVICE_MODEL_ENABLED
    layer = settings.SERVICE_MODEL_ENABLED
