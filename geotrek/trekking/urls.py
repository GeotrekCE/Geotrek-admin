from django.conf import settings
from django.urls import path, register_converter

from mapentity.registry import registry

from geotrek.altimetry.urls import AltimetryEntityOptions
from geotrek.common.urls import PublishableEntityOptions, LangConverter
from mapentity.registry import MapEntityOptions

from . import models
from .views import (
    TrekDocumentPublic, TrekBookletDocumentPublic, TrekMapImage, TrekMarkupPublic,
    TrekGPXDetail, TrekKMLDetail, WebLinkCreatePopup,
    CirkwiTrekView, CirkwiPOIView, TrekPOIViewSet,
    SyncRandoRedirect, TrekServiceViewSet, sync_view,
    sync_update_json
)

register_converter(LangConverter, 'lang')

app_name = 'trekking'
urlpatterns = [
    path('api/<lang:lang>/treks/<int:pk>/pois.geojson', TrekPOIViewSet.as_view({'get': 'list'}), name="trek_poi_geojson"),
    path('api/<lang:lang>/treks/<int:pk>/services.geojson', TrekServiceViewSet.as_view({'get': 'list'}), name="trek_service_geojson"),
    path('api/<lang:lang>/treks/<int:pk>/<slug:slug>.gpx', TrekGPXDetail.as_view(), name="trek_gpx_detail"),
    path('api/<lang:lang>/treks/<int:pk>/<slug:slug>.kml', TrekKMLDetail.as_view(), name="trek_kml_detail"),
    path('api/<lang:lang>/treks/<int:pk>/meta.html', TrekKMLDetail.as_view(), name="trek_meta"),
    path('popup/add/weblink/', WebLinkCreatePopup.as_view(), name='weblink_add'),
    path('api/cirkwi/circuits.xml', CirkwiTrekView.as_view()),
    path('api/cirkwi/pois.xml', CirkwiPOIView.as_view()),
    path('commands/sync', SyncRandoRedirect.as_view(), name='sync_randos'),
    path('commands/syncview', sync_view, name='sync_randos_view'),
    path('commands/statesync/', sync_update_json, name='sync_randos_state'),
    path('image/trek-<int:pk>-<lang:lang>.png', TrekMapImage.as_view(), name='trek_map_image'),
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
    document_public_booklet_view = TrekBookletDocumentPublic
    markup_public_view = TrekMarkupPublic


class POIEntityOptions(PublishableEntityOptions):
    pass


class ServiceEntityOptions(MapEntityOptions):
    pass


urlpatterns += registry.register(models.Trek, TrekEntityOptions, menu=settings.TREKKING_MODEL_ENABLED)
urlpatterns += registry.register(models.POI, POIEntityOptions, menu=settings.POI_MODEL_ENABLED)
urlpatterns += registry.register(models.Service, ServiceEntityOptions, menu=settings.SERVICE_MODEL_ENABLED)
