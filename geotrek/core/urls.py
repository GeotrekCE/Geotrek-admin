from django.conf.urls import patterns, url

from mapentity import registry

from .models import Path, Trail
from .views import (
    ElevationChart,
    get_graph_json,
)


urlpatterns = patterns('',
    url(r'^api/graph.json$', get_graph_json, name="path_json_graph"),
    url(r'^api/path/(?P<pk>\d+)/profile.svg$', ElevationChart.as_view(model=Path), name='path_profile_svg'),
)

urlpatterns += registry.register(Path)
urlpatterns += registry.register(Trail, menu=False)
