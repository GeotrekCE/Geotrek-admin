from django.conf.urls import patterns, url

from mapentity import registry

from geotrek.altimetry.views import (ElevationProfile, ElevationChart,
                                     ElevationArea)
from . import models
from .views import (
    TrekDocumentPublic, TrekPrint,
    TrekJsonDetail, TrekGPXDetail, TrekKMLDetail, TrekPOIGeoJSON,
    WebLinkCreatePopup
)


urlpatterns = patterns('',
    url(r'^document/print-trek-(?P<pk>\d+).odt$', TrekDocumentPublic.as_view(), name="trek_document_public"),
    url(r'^api/trek/trek-(?P<pk>\d+).pdf$', TrekPrint.as_view(), name="trek_printable"),

    url(r'^api/trek/trek-(?P<pk>\d+).json$', TrekJsonDetail.as_view(), name="trek_json_detail"),
    url(r'^api/trek/trek-(?P<pk>\d+).gpx$', TrekGPXDetail.as_view(), name="trek_gpx_detail"),
    url(r'^api/trek/trek-(?P<pk>\d+).kml$', TrekKMLDetail.as_view(), name="trek_kml_detail"),
    url(r'^api/trek/(?P<pk>\d+)/profile.json$', ElevationProfile.as_view(model=models.Trek), name="trek_profile"),
    url(r'^api/trek/(?P<pk>\d+)/dem.json$', ElevationArea.as_view(model=models.Trek), name="trek_elevation_area"),
    url(r'^api/trek/(?P<pk>\d+)/profile.svg$', ElevationChart.as_view(model=models.Trek), name='trek_profile_svg'),
    url(r'^api/trek/(?P<pk>\d+)/pois.geojson$', TrekPOIGeoJSON.as_view(), name="trek_poi_geojson"),
    url(r'^popup/add/weblink/', WebLinkCreatePopup.as_view(), name='weblink_add'),
)

urlpatterns += registry.register(models.Trek)
urlpatterns += registry.register(models.POI)
