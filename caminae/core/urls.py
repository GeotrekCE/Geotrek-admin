from django.conf.urls import patterns, url

from .views import PathList


urlpatterns = patterns('',
    url(r'^path.geojson$', PathList.as_view(), name="layerpath"),
)
