from django.conf import settings
from django.urls import path, register_converter
from mapentity.registry import registry

from geotrek.common.urls import LangConverter
from geotrek.trekking.views import TrekInfrastructureViewSet
from . import models

register_converter(LangConverter, 'lang')

app_name = 'infrastructure'

urlpatterns = registry.register(models.Infrastructure, menu=settings.INFRASTRUCTURE_MODEL_ENABLED)


urlpatterns += [
    path('api/<lang:lang>/treks/<int:pk>/infrastructures.geojson',
         TrekInfrastructureViewSet.as_view({'get': 'list'}), name="trek_infrastructure_geojson"),
]
