from django.conf.urls import patterns, url

from mapentity import registry

from geotrek.altimetry.urls import AltimetryEntityOptions
from geotrek.common.urls import PublishableEntityOptions

from . import models
from .views import (
    TrekDocumentPublic, POIDocumentPublic,
    TrekGPXDetail, TrekKMLDetail, WebLinkCreatePopup,
    CirkwiTrekView, CirkwiPOIView, TrekPOIViewSet
)
from . import serializers as trekking_serializers


urlpatterns = patterns(
    '',
    url(r'^api/treks/(?P<pk>\d+)/pois\.geojson$', TrekPOIViewSet.as_view({'get': 'list'}), name="trek_poi_geojson"),
    url(r'^api/treks/(?P<pk>\d+)/(?P<slug>[-_\w]+).gpx$', TrekGPXDetail.as_view(), name="trek_gpx_detail"),
    url(r'^api/treks/(?P<pk>\d+)/(?P<slug>[-_\w]+).kml$', TrekKMLDetail.as_view(), name="trek_kml_detail"),
    url(r'^popup/add/weblink/', WebLinkCreatePopup.as_view(), name='weblink_add'),
    url(r'^api/cirkwi/circuits.xml', CirkwiTrekView.as_view()),
    url(r'^api/cirkwi/pois.xml', CirkwiPOIView.as_view()),
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


urlpatterns += registry.register(models.Trek, TrekEntityOptions)
urlpatterns += registry.register(models.POI, POIEntityOptions)
