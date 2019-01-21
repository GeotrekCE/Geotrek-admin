from django.conf import settings
from django.conf.urls import url

from mapentity.registry import registry

from geotrek.altimetry.urls import AltimetryEntityOptions
from geotrek.core.models import Path, Trail
from geotrek.core.views import (
    get_graph_json, merge_path, ParametersView, PathGPXDetail, PathKMLDetail, TrailGPXDetail, TrailKMLDetail
)

urlpatterns = [
    url(r'^api/graph.json$', get_graph_json, name="path_json_graph"),
    url(r'^api/(?P<lang>\w\w)/parameters.json$', ParametersView.as_view(), name='parameters_json'),
    url(r'^mergepath/$', merge_path, name="merge_path"),
    url(r'^api/(?P<lang>\w\w)/paths/(?P<pk>\d+)/path_(?P<slug>[-_\w]+).gpx$', PathGPXDetail.as_view(),
        name="path_gpx_detail"),
    url(r'^api/(?P<lang>\w\w)/paths/(?P<pk>\d+)/path_(?P<slug>[-_\w]+).kml$', PathKMLDetail.as_view(),
        name="path_kml_detail"),
    url(r'^api/(?P<lang>\w\w)/trails/(?P<pk>\d+)/trail_(?P<slug>[-_\w]+).gpx$', TrailGPXDetail.as_view(),
        name="trail_gpx_detail"),
    url(r'^api/(?P<lang>\w\w)/trails/(?P<pk>\d+)/trail_(?P<slug>[-_\w]+).kml$', TrailKMLDetail.as_view(),
        name="trail_kml_detail"),
]


class PathEntityOptions(AltimetryEntityOptions):
    def get_queryset(self):
        qs = super(PathEntityOptions, self).get_queryset()
        qs = qs.prefetch_related('networks', 'usages')
        return qs


urlpatterns += registry.register(Path, PathEntityOptions, menu=settings.TREKKING_TOPOLOGY_ENABLED)
urlpatterns += registry.register(Trail, menu=settings.TRAIL_MODEL_ENABLED)
