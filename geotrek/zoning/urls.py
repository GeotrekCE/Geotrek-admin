from django.conf.urls import patterns, url
from . import views


urlpatterns = patterns(
    '',
    url(r'^api/city/city.geojson$', views.CityGeoJSONLayer.as_view(), name="city_layer"),
    url(r'^api/restrictedarea/restrictedarea.geojson$', views.RestrictedAreaGeoJSONLayer.as_view(), name="restrictedarea_layer"),
    url(r'^api/restrictedarea/type/(?P<type_pk>\d+)/restrictedarea.geojson$', views.RestrictedAreaTypeGeoJSONLayer.as_view(), name="restrictedarea_type_layer"),
    url(r'^api/district/district.geojson$', views.DistrictGeoJSONLayer.as_view(), name="district_layer"),
)
