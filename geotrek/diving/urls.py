from django.urls import path, register_converter
from mapentity.registry import registry

from geotrek.common.urls import LangConverter

from . import entities, models, views

register_converter(LangConverter, "lang")

app_name = "diving"

urlpatterns = [
    path(
        "image/dive-<int:pk>-<lang:lang>.png",
        views.DiveMapImage.as_view(),
        name="dive_map_image",
    ),
]

urlpatterns += registry.register(models.Dive, options=entities.DiveEntityOptions)
