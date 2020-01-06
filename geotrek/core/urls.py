from django.conf import settings
from django.urls import path, re_path

from mapentity.registry import registry

from geotrek.altimetry.urls import AltimetryEntityOptions
from geotrek.core.models import Path, Trail
from geotrek.core.views import (
    get_graph_json, merge_path, ParametersView, PathGPXDetail, PathKMLDetail, TrailGPXDetail, TrailKMLDetail,
    MultiplePathDelete
)

app_name = 'core'
urlpatterns = [
    path('api/graph.json', get_graph_json, name="path_json_graph"),
    path('api/<str:lang>/parameters.json', ParametersView.as_view(), name='parameters_json'),
    path('mergepath/', merge_path, name="merge_path"),
    re_path(r'^path/delete/(?P<pk>\d+(,\d+)+)/', MultiplePathDelete.as_view(), name="multiple_path_delete"),
    path('api/<str:lang>/paths/<int:pk>/path_<slug:slug>.gpx', PathGPXDetail.as_view(),
         name="path_gpx_detail"),
    path('api/<str:lang>/paths/<int:pk>/path_<slug:slug>.kml', PathKMLDetail.as_view(),
         name="path_kml_detail"),
    path('api/<str:lang>/trails/<int:pk>/trail_<slug:slug>.gpx', TrailGPXDetail.as_view(),
         name="trail_gpx_detail"),
    path('api/<str:lang>/trails/<int:pk>/trail_<slug:slug>.kml', TrailKMLDetail.as_view(),
         name="trail_kml_detail"),
]


class PathEntityOptions(AltimetryEntityOptions):
    def get_queryset(self):
        qs = super(PathEntityOptions, self).get_queryset()
        qs = qs.prefetch_related('networks', 'usages')
        return qs


urlpatterns += registry.register(Path, PathEntityOptions, menu=(settings.PATH_MODEL_ENABLED and settings.TREKKING_TOPOLOGY_ENABLED))
urlpatterns += registry.register(Trail, menu=(settings.TRAIL_MODEL_ENABLED and settings.TREKKING_TOPOLOGY_ENABLED))
