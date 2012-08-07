from django.conf.urls import patterns, url

from .views import (
    PathLayer, PathList, PathDetail, PathCreate,
    PathUpdate, PathDelete, PathJsonList, ElevationProfile,
    get_graph_json,
)


urlpatterns = patterns('',
    url(r'^data/paths.geojson$', PathLayer.as_view(), name="path_layer"),
    url(r'^data/paths.json$', PathJsonList.as_view(), name="path_json_list"),
    url(r'^data/graph.json$', get_graph_json, name="path_json_graph"),
)

urlpatterns += patterns('',
    url(r'^path/list/$', PathList.as_view(), name="path_list"),
    url(r'^path/add/$', PathCreate.as_view(), name='path_add'),
    url(r'^path/(?P<pk>\d+)/$', PathDetail.as_view(), name='path_detail'),
    url(r'^path/edit/(?P<pk>\d+)/$', PathUpdate.as_view(), name='path_update'),
    url(r'^path/delete/(?P<pk>\d+)$', PathDelete.as_view(), name='path_delete'),

    # Specific
    url(r'^path/(?P<pk>\d+)/profile/$', ElevationProfile.as_view(), name='path_profile'),
)
