from django.urls import path, re_path, register_converter
from mapentity.registry import registry

from geotrek.common.urls import LangConverter

from . import entities, models, views

register_converter(LangConverter, "lang")

app_name = "tourism"
urlpatterns = [
    re_path(
        r"^api/(?P<lang>[a-z]{2}(-[a-z]{2,4})?)/treks/(?P<pk>\d+)/information_desks.geojson$",
        views.TrekInformationDeskViewSet.as_view({"get": "list"}),
        name="trek_information_desk_geojson",
    ),
    path(
        "popup/add/organizer/",
        views.TouristicEventOrganizerCreatePopup.as_view(),
        name="organizer_add",
    ),
]

urlpatterns += registry.register(
    models.TouristicEvent,
    options=entities.TouristicEventEntityOptions,
)
urlpatterns += registry.register(
    models.TouristicContent,
    options=entities.TouristicContentEntityOptions,
)
