from django.conf.urls import patterns, url

from mapentity import registry

from geotrek.altimetry.urls import AltimetryEntityOptions
from geotrek.common.urls import PublishableEntityOptions

from . import models
from .views import (
    TrekDocumentPublic,
    TrekJsonDetail, TrekGPXDetail, TrekKMLDetail, TrekPOIGeoJSON,
    TrekInformationDeskGeoJSON, WebLinkCreatePopup
)


urlpatterns = patterns('',
    url(r'^api/trek/trek-(?P<pk>\d+).json$', TrekJsonDetail.as_view(), name="trek_json_detail"),
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


class POIEntityOptions(PublishableEntityOptions):
    pass

urlpatterns += registry.register(models.Trek, TrekEntityOptions)
urlpatterns += registry.register(models.POI, POIEntityOptions)
