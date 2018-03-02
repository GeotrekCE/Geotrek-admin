from django.conf.urls import url

from mapentity.registry import registry

from geotrek.common.urls import PublishableEntityOptions

from . import models
from . import serializers
from . import views


class SensitiveAreaEntityOptions(PublishableEntityOptions):
    def get_serializer(self):
        return serializers.SensitiveAreaSerializer

    def get_queryset(self):
        return self.model.objects.existing()


urlpatterns = [
    url(r'^api/(?P<lang>\w\w)/treks/(?P<pk>\d+)/sensitiveareas\.geojson$',
        views.TrekSensitiveAreaViewSet.as_view({'get': 'list'}),
        name="trek_sensitivearea_geojson"),
    url(r'^api/(?P<lang>\w\w)/sensitiveareas/(?P<pk>\d+).kml$',
        views.SensitiveAreaKMLDetail.as_view(), name="sensitivearea_kml_detail"),
]
urlpatterns += registry.register(models.SensitiveArea, SensitiveAreaEntityOptions)
