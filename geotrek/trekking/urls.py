from django.conf.urls import patterns, url
from django.views.generic import RedirectView

from mapentity import registry

from geotrek.altimetry.urls import AltimetryEntityOptions
from geotrek.common.urls import PublishableEntityOptions

from . import models
from .views import (
    TrekDocumentPublic, POIDocumentPublic,
    TrekGPXDetail, TrekKMLDetail, TrekPOIGeoJSON,
    TrekInformationDeskGeoJSON, WebLinkCreatePopup
)
from . import serializers as trekking_serializers


urlpatterns = patterns('',
    # Retro-compat for Geotrek-rando <= 1.31
    url(r'^api/trek/trek-(?P<pk>\d+).json$', RedirectView.as_view(url='/api/treks/%(pk)s/')),

    # Trek specific
    url(r'^api/trek/trek-(?P<pk>\d+).gpx$', TrekGPXDetail.as_view(), name="trek_gpx_detail"),
    url(r'^api/trek/trek-(?P<pk>\d+).kml$', TrekKMLDetail.as_view(), name="trek_kml_detail"),
    url(r'^api/trek/(?P<pk>\d+)/pois.geojson$', TrekPOIGeoJSON.as_view(), name="trek_poi_geojson"),
    url(r'^api/trek/(?P<pk>\d+)/information_desks.geojson$', TrekInformationDeskGeoJSON.as_view(), name="trek_information_desk_geojson"),
    url(r'^popup/add/weblink/', WebLinkCreatePopup.as_view(), name='weblink_add'),
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
