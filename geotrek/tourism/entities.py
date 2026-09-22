from django.conf import settings

from geotrek.common.mixins.entity_options import PublishableEntityOptions
from geotrek.tourism import views as tourism_views


class TouristicContentEntityOptions(PublishableEntityOptions):
    document_public_view = tourism_views.TouristicContentDocumentPublic
    document_public_booklet_view = tourism_views.TouristicContentDocumentBookletPublic
    markup_public_view = tourism_views.TouristicContentMarkupPublic
    menu = settings.TOURISM_ENABLED and settings.TOURISTICCONTENT_MODEL_ENABLED
    layer = settings.TOURISM_ENABLED and settings.TOURISTICCONTENT_MODEL_ENABLED


class TouristicEventEntityOptions(PublishableEntityOptions):
    document_public_view = tourism_views.TouristicEventDocumentPublic
    document_public_booklet_view = tourism_views.TouristicEventDocumentBookletPublic
    markup_public_view = tourism_views.TouristicEventMarkupPublic
    menu = settings.TOURISM_ENABLED and settings.TOURISTICEVENT_MODEL_ENABLED
    layer = settings.TOURISM_ENABLED and settings.TOURISTICEVENT_MODEL_ENABLED
