from django.urls import path, register_converter
from mapentity.registry import registry

from geotrek.common.urls import LangConverter

from . import entities, models, views

register_converter(LangConverter, "lang")

app_name = "trekking"
urlpatterns = [
    path(
        "api/<lang:lang>/treks/<int:pk>/pois.geojson",
        views.TrekPOIViewSet.as_view({"get": "list"}),
        name="trek_poi_geojson",
    ),
    path(
        "api/<lang:lang>/treks/<int:pk>/services.geojson",
        views.TrekServiceViewSet.as_view({"get": "list"}),
        name="trek_service_geojson",
    ),
    path(
        "api/<lang:lang>/treks/<int:pk>/<slug:slug>.gpx",
        views.TrekGPXDetail.as_view(),
        name="trek_gpx_detail",
    ),
    path(
        "api/<lang:lang>/treks/<int:pk>/<slug:slug>.kml",
        views.TrekKMLDetail.as_view(),
        name="trek_kml_detail",
    ),
    path("popup/add/weblink/", views.WebLinkCreatePopup.as_view(), name="weblink_add"),
    path(
        "image/trek-<int:pk>-<lang:lang>.png",
        views.TrekMapImage.as_view(),
        name="trek_map_image",
    ),
]

urlpatterns += registry.register(models.Trek, options=entities.TrekEntityOptions)
urlpatterns += registry.register(models.POI, options=entities.POIEntityOptions)
urlpatterns += registry.register(models.Service, options=entities.ServiceEntityOptions)
