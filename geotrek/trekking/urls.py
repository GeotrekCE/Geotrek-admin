from django.conf.urls import patterns, url

from mapentity import registry

from geotrek.altimetry.urls import AltimetryEntityOptions
from geotrek.common.urls import PublishableEntityOptions
from mapentity.registry import MapEntityOptions

from . import models
from .views import (
    TrekDocumentPublic, POIDocumentPublic, TrekMapImage,
    TrekGPXDetail, TrekKMLDetail, WebLinkCreatePopup,
    CirkwiTrekView, CirkwiPOIView, TrekPOIViewSet,
    SyncRandoRedirect, TrekServiceViewSet, sync_view,
    sync_update_json
)
from . import serializers as trekking_serializers


urlpatterns = patterns(
    '',
    url(r'^api/(?P<lang>\w\w)/treks/(?P<pk>\d+)/pois\.geojson$', TrekPOIViewSet.as_view({'get': 'list'}), name="trek_poi_geojson"),
    url(r'^api/(?P<lang>\w\w)/treks/(?P<pk>\d+)/services\.geojson$', TrekServiceViewSet.as_view({'get': 'list'}), name="trek_service_geojson"),
    url(r'^api/(?P<lang>\w\w)/treks/(?P<pk>\d+)/(?P<slug>[-_\w]+).gpx$', TrekGPXDetail.as_view(), name="trek_gpx_detail"),
    url(r'^api/(?P<lang>\w\w)/treks/(?P<pk>\d+)/(?P<slug>[-_\w]+).kml$', TrekKMLDetail.as_view(), name="trek_kml_detail"),
    url(r'^popup/add/weblink/', WebLinkCreatePopup.as_view(), name='weblink_add'),
    url(r'^api/cirkwi/circuits.xml', CirkwiTrekView.as_view()),
    url(r'^api/cirkwi/pois.xml', CirkwiPOIView.as_view()),
    url(r'^commands/sync$', SyncRandoRedirect.as_view(), name='sync_randos'),
    url(r'^commands/syncview$', sync_view, name='sync_randos_view'),
    url(r'^commands/statesync/$', sync_update_json, name='sync_randos_state'),
    url(r'^image/trek-(?P<pk>\d+)-(?P<lang>\w\w).png$', TrekMapImage.as_view(), name='trek_map_image'),
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

    def get_serializer(self):
        return trekking_serializers.TrekSerializer

    def get_queryset(self):
        return self.model.objects.existing()


class POIEntityOptions(PublishableEntityOptions):
    document_public_view = POIDocumentPublic

    def get_serializer(self):
        return trekking_serializers.POISerializer


class ServiceEntityOptions(MapEntityOptions):

    def get_serializer(self):
        return trekking_serializers.ServiceSerializer


urlpatterns += registry.register(models.Trek, TrekEntityOptions)
urlpatterns += registry.register(models.POI, POIEntityOptions)
urlpatterns += registry.register(models.Service, ServiceEntityOptions)
