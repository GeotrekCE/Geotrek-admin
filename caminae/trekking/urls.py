from django.conf.urls import patterns, url

from .views import (
    TrekLayer, TrekList, TrekDetail, TrekDocument, TrekCreate,
    TrekUpdate, TrekDelete, TrekJsonList, TrekFormatList,
    POILayer, POIList, POIDetail, POIDocument, POICreate,
    POIUpdate, POIDelete, POIJsonList, POIFormatList,
    TrekJsonDetail, TrekJsonProfile,

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
    url(r'^api/trek/(?P<pk>\d+)/profile/$', TrekJsonProfile.as_view(), name="trek_json_profile"),
    url(r'^popup/add/weblink/', WebLinkCreatePopup.as_view(), name='weblink_add'),
)
