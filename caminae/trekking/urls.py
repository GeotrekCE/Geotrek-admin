from django.conf.urls import patterns, url

from .views import (
    TrekLayer, TrekList, TrekDetail, TrekDocument, TrekCreate,
    TrekUpdate, TrekDelete, TrekJsonList, TrekFormatList,
    POILayer, POIList, POIDetail, POIDocument, POICreate,
    POIUpdate, POIDelete, POIJsonList, POIFormatList,
    TrekJsonDetail, TrekGPXDetail, TrekKMLDetail, TrekJsonProfile, TrekPOIGeoJSON,
    WebLinkCreatePopup
)

from caminae.mapentity.urlizor import view_classes_to_url


urlpatterns = patterns('', *view_classes_to_url(
    TrekLayer, TrekList, TrekDetail, TrekDocument, TrekCreate,
    TrekUpdate, TrekDelete, TrekJsonList, TrekFormatList,
    POILayer, POIList, POIDetail, POIDocument, POICreate,
    POIUpdate, POIDelete, POIJsonList, POIFormatList,
))

urlpatterns += patterns('',
    url(r'^api/trek/trek-(?P<pk>\d+).json$', TrekJsonDetail.as_view(), name="trek_json_detail"),
    url(r'^api/trek/trek-(?P<pk>\d+).gpx$', TrekGPXDetail.as_view(), name="trek_gpx_detail"),
    url(r'^api/trek/trek-(?P<pk>\d+).kml$', TrekKMLDetail.as_view(), name="trek_kml_detail"),
    url(r'^api/trek/(?P<pk>\d+)/profile.json$', TrekJsonProfile.as_view(), name="trek_profile"),
    url(r'^api/trek/(?P<pk>\d+)/pois.geojson$', TrekPOIGeoJSON.as_view(), name="trek_poi_geojson"),
    url(r'^popup/add/weblink/', WebLinkCreatePopup.as_view(), name='weblink_add'),
)
