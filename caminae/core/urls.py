from django.conf.urls import patterns, url

from .views import (
    PathLayer, PathList, PathDetail, PathCreate,
    PathUpdate, PathDelete, PathJsonList, PathFormatList,
    ElevationProfile,
    get_graph_json,
    TrailDetail,
)

from caminae.mapentity.urlizor import view_classes_to_url


urlpatterns = patterns('',
    url(r'^api/graph.json$', get_graph_json, name="path_json_graph"),
    # Specific
    url(r'^api/path/(?P<pk>\d+)/profile/$', ElevationProfile.as_view(), name='path_profile'),
)

urlpatterns += patterns('', *view_classes_to_url(
    PathList, PathCreate, PathDetail, PathUpdate,
    PathDelete, PathLayer, PathJsonList, PathFormatList, TrailDetail
))
