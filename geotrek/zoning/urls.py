from django.urls import path

from . import views

app_name = "zoning"

urlpatterns = [
    path(
        "api/city/city.geojson", views.CityGeoJSONAPIView.as_view(), name="city_layer"
    ),
    path(
        "api/restrictedarea/restrictedarea.geojson",
        views.RestrictedAreaGeoJSONAPIView.as_view(),
        name="restrictedarea_layer",
    ),
    path(
        "api/restrictedarea/type/<int:type_pk>/restrictedarea.geojson",
        views.RestrictedAreaTypeGeoJSONLayer.as_view(),
        name="restrictedarea_type_layer",
    ),
    path(
        "api/district/district.geojson",
        views.DistrictGeoJSONAPIView.as_view(),
        name="district_layer",
    ),
]
