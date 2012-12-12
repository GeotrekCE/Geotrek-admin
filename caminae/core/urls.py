from django.conf.urls import patterns, url

from .views import (
    PathLayer, PathList, PathDetail, PathDocument, PathCreate,
    PathUpdate, PathDelete, PathJsonList, PathFormatList,
    ElevationProfile,
    get_graph_json,
    TrailDetail, TrailDocument,
)

from caminae.mapentity.urlizor import view_classes_to_url


urlpatterns = patterns('',
    url(r'^api/graph.json$', get_graph_json, name="path_json_graph"),
    url(r'^api/path/(?P<pk>\d+)/profile.json$', ElevationProfile.as_view(), name='path_profile'),
)

urlpatterns += patterns('', *view_classes_to_url(
    PathList, PathCreate, PathDetail, PathDocument, PathUpdate,
    PathDelete, PathLayer, PathJsonList, PathFormatList, 
    TrailDetail, TrailDocument
))
