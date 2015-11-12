from django.conf import settings
from django.conf.urls import patterns, url

from mapentity import registry

from geotrek.altimetry.urls import AltimetryEntityOptions
from geotrek.core.models import Path, Trail
from geotrek.core.views import get_graph_json, get_bound_force_osm


urlpatterns = patterns(
    '',
    url(r'^api/graph.json$', get_graph_json, name="path_json_graph"),
    url(r'^force_osm_baselayer_bound.json$', get_bound_force_osm, name="force_osm_baselayer_bound"),
)


class PathEntityOptions(AltimetryEntityOptions):
    # Profiles for paths
    pass


urlpatterns += registry.register(Path, PathEntityOptions, menu=settings.TREKKING_TOPOLOGY_ENABLED)
urlpatterns += registry.register(Trail, menu=settings.TRAIL_MODEL_ENABLED)
