from django.conf.urls import patterns, url

from .views import (
    PathLayer, PathList, PathDetail, PathCreate,
    PathUpdate, PathDelete, PathJsonList, ElevationProfile,
    get_graph_json,
)

from caminae.core.entity import view_classes_to_url


urlpatterns = patterns('',
    url(r'^data/graph.json$', get_graph_json, name="path_json_graph"),
    # Specific
    url(r'^path/(?P<pk>\d+)/profile/$', ElevationProfile.as_view(), name='path_profile'),
)

view_classes = (
    PathList, PathCreate, PathDetail, PathUpdate,
    PathDelete, PathLayer, PathJsonList
)
urlpatterns += patterns('', *view_classes_to_url(*view_classes))
