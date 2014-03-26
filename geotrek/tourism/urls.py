from django.conf.urls import patterns, url

from .views import DataSourceList


urlpatterns = patterns('',
    url(r'^api/datasource/datasources.json$', DataSourceList.as_view(), name="datasource_list_json"),
)
