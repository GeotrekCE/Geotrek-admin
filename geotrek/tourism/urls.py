from django.conf.urls import patterns, url

from mapentity import registry

from . import models
from .views import DataSourceList, DataSourceGeoJSON, InformationDeskGeoJSON


urlpatterns = patterns(
    '',
    url(r'^api/datasource/datasources.json$', DataSourceList.as_view(), name="datasource_list_json"),
    url(r'^api/datasource/datasource-(?P<pk>\d+).geojson$', DataSourceGeoJSON.as_view(), name="datasource_geojson"),
    url(r'^api/informationdesk/informationdesk.geojson$', InformationDeskGeoJSON.as_view(), name="informationdesk_geojson"),
)

urlpatterns += registry.register(models.TouristicContent)
