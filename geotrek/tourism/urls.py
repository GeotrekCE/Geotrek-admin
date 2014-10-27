from django.conf import settings
from django.conf.urls import patterns, url

from mapentity import registry

from geotrek.common.urls import PublishableEntityOptions

from . import models
from .views import DataSourceList, DataSourceGeoJSON, InformationDeskGeoJSON


urlpatterns = patterns(
    '',
    url(r'^api/datasource/datasources.json$', DataSourceList.as_view(), name="datasource_list_json"),
    url(r'^api/datasource/datasource-(?P<pk>\d+).geojson$', DataSourceGeoJSON.as_view(), name="datasource_geojson"),
    url(r'^api/informationdesk/informationdesk.geojson$', InformationDeskGeoJSON.as_view(), name="informationdesk_geojson"),
)
from . import serializers as tourism_serializers


class TouristicContentEntityOptions(PublishableEntityOptions):
    def get_serializer(self):
        return tourism_serializers.TouristicContentSerializer

    def get_queryset(self):
        return self.model.objects.existing()

if settings.TOURISM_ENABLED:
    urlpatterns += registry.register(models.TouristicContent, TouristicContentEntityOptions)


class TouristicEventEntityOptions(PublishableEntityOptions):
    def get_serializer(self):
        return tourism_serializers.TouristicEventSerializer

    def get_queryset(self):
        return self.model.objects.existing()

if settings.TOURISM_ENABLED:
    urlpatterns += registry.register(models.TouristicEvent, TouristicEventEntityOptions)
