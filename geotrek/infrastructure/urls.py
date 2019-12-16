from django.conf import settings
from django.conf.urls import url

from mapentity.registry import registry

from . import models
from geotrek.trekking.views import TrekInfrastructureViewSet


app_name = 'infrastructure'
urlpatterns = registry.register(models.Infrastructure, menu=settings.INFRASTRUCTURE_MODEL_ENABLED)
urlpatterns += [
    url(r'^api/(?P<lang>\w\w)/treks/(?P<pk>\d+)/infrastructures\.geojson$',
        TrekInfrastructureViewSet.as_view({'get': 'list'}), name="trek_infrastructure_geojson"),
]
