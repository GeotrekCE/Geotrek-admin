from django.conf import settings
from django.urls import path, register_converter
from mapentity.registry import MapEntityOptions, registry

from geotrek.altimetry.urls import AltimetryEntityOptions
from geotrek.common.urls import LangConverter, PublishableEntityOptions

from . import models
from .views import (
    TrekDocumentBookletPublic,
    TrekDocumentPublic,
    TrekGPXDetail,
    TrekKMLDetail,
    TrekMapImage,
    TrekMarkupPublic,
    TrekPOIViewSet,
    TrekServiceViewSet,
    WebLinkCreatePopup,
    POIOSMCompare,
    POIOSMValidate,
)

register_converter(LangConverter, "lang")

app_name = "trekking"
urlpatterns = [
    path(
        "api/<lang:lang>/treks/<int:pk>/pois.geojson",
        TrekPOIViewSet.as_view({"get": "list"}),
        name="trek_poi_geojson",
    ),
    path(
        "api/<lang:lang>/treks/<int:pk>/services.geojson",
        TrekServiceViewSet.as_view({"get": "list"}),
        name="trek_service_geojson",
    ),
    path(
        "api/<lang:lang>/treks/<int:pk>/<slug:slug>.gpx",
        TrekGPXDetail.as_view(),
        name="trek_gpx_detail",
    ),
    path(
        "api/<lang:lang>/treks/<int:pk>/<slug:slug>.kml",
        TrekKMLDetail.as_view(),
        name="trek_kml_detail",
    ),
    path("popup/add/weblink/", WebLinkCreatePopup.as_view(), name="weblink_add"),
    path(
        "image/trek-<int:pk>-<lang:lang>.png",
        TrekMapImage.as_view(),
        name="trek_map_image",
    ),
    path("poi/<int:pk>/osm/", POIOSMCompare.as_view(), name="poi_osm_compare"),
    path("poi/<int:pk>/osm/validate", POIOSMValidate.as_view(), name="poi_osm_validate"),
]


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


class POIEntityOptions(PublishableEntityOptions):
    pass


class ServiceEntityOptions(MapEntityOptions):
    pass


urlpatterns += registry.register(
    models.Trek, TrekEntityOptions, menu=settings.TREKKING_MODEL_ENABLED
)
urlpatterns += registry.register(
    models.POI, POIEntityOptions, menu=settings.POI_MODEL_ENABLED
)
urlpatterns += registry.register(
    models.Service, ServiceEntityOptions, menu=settings.SERVICE_MODEL_ENABLED
)
