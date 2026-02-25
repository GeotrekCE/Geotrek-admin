from django.urls import path, register_converter
from mapentity.registry import registry

from geotrek.common.urls import LangConverter

from . import entities, models, views

register_converter(LangConverter, "lang")

app_name = "core"

urlpatterns = [
    path(
        "api/<lang:lang>/paths/<int:pk>/path_<slug:slug>.gpx",
        views.PathGPXDetail.as_view(),
        name="path_gpx_detail",
    ),
    path(
        "api/<lang:lang>/paths/<int:pk>/path_<slug:slug>.kml",
        views.PathKMLDetail.as_view(),
        name="path_kml_detail",
    ),
    path(
        "api/<lang:lang>/trails/<int:pk>/trail_<slug:slug>.gpx",
        views.TrailGPXDetail.as_view(),
        name="trail_gpx_detail",
    ),
    path(
        "api/<lang:lang>/trails/<int:pk>/trail_<slug:slug>.kml",
        views.TrailKMLDetail.as_view(),
        name="trail_kml_detail",
    ),
]

urlpatterns += registry.register(
    models.Path,
    options=entities.PathEntityOptions,
)
urlpatterns += registry.register(models.Trail, options=entities.TrailEntityOptions)
