from django.conf.urls import patterns, url

from mapentity import registry

from .models import Path, Trail
from .views import (
    ElevationProfile,
    get_graph_json,
)


urlpatterns = patterns('',
    url(r'^api/graph.json$', get_graph_json, name="path_json_graph"),
    url(r'^api/path/(?P<pk>\d+)/profile.json$', ElevationProfile.as_view(), name='path_profile'),
)

urlpatterns += registry.register(Path)
urlpatterns += registry.register(Trail, menu=False)
