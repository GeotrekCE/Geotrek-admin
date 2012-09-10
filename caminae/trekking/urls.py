from django.conf.urls import patterns, url

from .views import (
    TrekLayer, TrekList, TrekDetail, TrekCreate,
    TrekUpdate, TrekDelete, TrekJsonList, TrekFormatList,
    POILayer, POIList, POIDetail, POICreate,
    POIUpdate, POIDelete, POIJsonList, POIFormatList,

    WebLinkCreatePopup
)

from caminae.mapentity.urlizor import view_classes_to_url


urlpatterns = patterns('', *view_classes_to_url(
    TrekLayer, TrekList, TrekDetail, TrekCreate,
    TrekUpdate, TrekDelete, TrekJsonList, TrekFormatList,
    POILayer, POIList, POIDetail, POICreate,
    POIUpdate, POIDelete, POIJsonList, POIFormatList,
))

urlpatterns += patterns('',
    url(r'^popup/add/weblink/', WebLinkCreatePopup.as_view(), name='weblink_add'),
)


