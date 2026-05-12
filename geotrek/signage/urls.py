from django.conf import settings
from django.urls import path, register_converter
from mapentity.registry import registry

from geotrek.common.urls import LangConverter
from geotrek.trekking.views import TrekSignageViewSet

from . import models

register_converter(LangConverter, "lang")

app_name = "signage"
urlpatterns = registry.register(models.Signage, menu=settings.SIGNAGE_MODEL_ENABLED)


if settings.BLADE_ENABLED:
    urlpatterns += registry.register(models.Blade, menu=False)


urlpatterns += [
    path(
        "api/<lang:lang>/treks/<int:pk>/signages.geojson",
        TrekSignageViewSet.as_view({"get": "list"}),
        name="trek_signage_geojson",
    ),
]
