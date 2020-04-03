from django.conf import settings
from django.urls import path, register_converter

from mapentity.registry import registry

from . import models
from geotrek.trekking.views import TrekInfrastructureViewSet
from geotrek.common.urls import LangConverter

register_converter(LangConverter, 'lang')

app_name = 'infrastructure'
urlpatterns = registry.register(models.Infrastructure, menu=settings.INFRASTRUCTURE_MODEL_ENABLED)
urlpatterns += [
    path('api/<lang:lang>/treks/<int:pk>/infrastructures.geojson',
         TrekInfrastructureViewSet.as_view({'get': 'list'}), name="trek_infrastructure_geojson"),
]
