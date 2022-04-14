from django.conf import settings
from django.db.models.functions import Round
from django.urls import path, re_path, register_converter
from mapentity.registry import registry

from geotrek.altimetry.urls import AltimetryEntityOptions
from geotrek.common.functions import Length
from geotrek.common.urls import LangConverter
from geotrek.common.views import ParametersView
from geotrek.core.models import Path, Trail
from geotrek.core.views import (
    get_graph_json, merge_path, PathGPXDetail, PathKMLDetail, TrailGPXDetail, TrailKMLDetail,
    MultiplePathDelete
)

register_converter(LangConverter, 'lang')

app_name = 'core'
urlpatterns = [
    path('api/graph.json', get_graph_json, name="path_json_graph"),
    path('api/<lang:lang>/parameters.json', ParametersView.as_view(), name='parameters_json'),
    path('mergepath/', merge_path, name="merge_path"),
    re_path(r'^path/delete/(?P<pk>\d+(,\d+)+)/', MultiplePathDelete.as_view(), name="multiple_path_delete"),
    path('api/<lang:lang>/paths/<int:pk>/path_<slug:slug>.gpx', PathGPXDetail.as_view(),
         name="path_gpx_detail"),
    path('api/<lang:lang>/paths/<int:pk>/path_<slug:slug>.kml', PathKMLDetail.as_view(),
         name="path_kml_detail"),
    path('api/<lang:lang>/trails/<int:pk>/trail_<slug:slug>.gpx', TrailGPXDetail.as_view(),
         name="trail_gpx_detail"),
    path('api/<lang:lang>/trails/<int:pk>/trail_<slug:slug>.kml', TrailKMLDetail.as_view(),
         name="trail_kml_detail"),
]


class PathEntityOptions(AltimetryEntityOptions):
    def get_queryset(self):
        return super().get_queryset().annotate(length_2d=Round(Length('geom'),
                                                               precision=1)).prefetch_related('networks', 'usages')


urlpatterns += registry.register(Path, PathEntityOptions, menu=(settings.PATH_MODEL_ENABLED and settings.TREKKING_TOPOLOGY_ENABLED))
urlpatterns += registry.register(Trail, menu=(settings.TRAIL_MODEL_ENABLED and settings.TREKKING_TOPOLOGY_ENABLED))
