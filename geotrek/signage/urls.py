from django.urls import path, register_converter
from mapentity.registry import registry

from geotrek.common.urls import LangConverter
from geotrek.trekking.views import TrekSignageViewSet

from . import entities, models

register_converter(LangConverter, "lang")

app_name = "signage"

urlpatterns = registry.register(models.Signage, options=entities.SignageEntityOptions)
urlpatterns += registry.register(models.Blade, options=entities.BladeEntityOptions)
urlpatterns += [
    path(
        "api/<lang:lang>/treks/<int:pk>/signages.geojson",
        TrekSignageViewSet.as_view({"get": "list"}),
        name="trek_signage_geojson",
    ),
]
