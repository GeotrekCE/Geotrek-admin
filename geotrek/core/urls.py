from django.conf import settings
from django.conf.urls import patterns, url

from mapentity import registry

from geotrek.altimetry.urls import AltimetryEntityOptions
from geotrek.core.models import Path, Trail
from geotrek.core.views import get_graph_json, merge_path, ParametersView


urlpatterns = patterns(
    '',
    url(r'^api/graph.json$', get_graph_json, name="path_json_graph"),
    url(r'^api/(?P<lang>\w\w)/parameters.json$', ParametersView.as_view(), name='parameters_json'),
    url(r'^mergepath/$', merge_path, name="merge_path"),
)


class PathEntityOptions(AltimetryEntityOptions):
    def get_queryset(self):
        qs = super(PathEntityOptions, self).get_queryset()
        qs = qs.prefetch_related('networks', 'usages')
        return qs


urlpatterns += registry.register(Path, PathEntityOptions, menu=settings.TREKKING_TOPOLOGY_ENABLED)
urlpatterns += registry.register(Trail, menu=settings.TRAIL_MODEL_ENABLED)
