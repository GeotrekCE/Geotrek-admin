from django.conf.urls import url

from mapentity.registry import registry

from . import models
from geotrek.trekking.views import TrekInfrastructureViewSet, TrekSignageViewSet


urlpatterns = registry.register(models.Infrastructure)
urlpatterns += registry.register(models.Signage)
urlpatterns += [
    url(r'^api/(?P<lang>\w\w)/treks/(?P<pk>\d+)/infrastructures\.geojson$',
        TrekInfrastructureViewSet.as_view({'get': 'list'}), name="trek_infrastructure_geojson"),
    url(r'^api/(?P<lang>\w\w)/treks/(?P<pk>\d+)/signages\.geojson$',
        TrekSignageViewSet.as_view({'get': 'list'}), name="trek_signage_geojson"),
]
