from django.conf.urls import url

from mapentity.registry import registry

from . import models
from geotrek.trekking.views import TrekSignageViewSet
from geotrek.signage.views import BladeUpdate

urlpatterns = registry.register(models.Signage)
urlpatterns += [
    url(r'^api/(?P<lang>\w\w)/treks/(?P<pk>\d+)/signages\.geojson$',
        TrekSignageViewSet.as_view({'get': 'list'}), name="trek_signage_geojson"),
    url(r'signage/blades/(?P<pk>\d+)/$', BladeUpdate.as_view(),
        name="blade_edit")
]
