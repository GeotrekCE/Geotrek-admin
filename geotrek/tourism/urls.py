from django.conf import settings
from django.urls import path, re_path, register_converter

from mapentity.registry import registry

from geotrek.common.urls import PublishableEntityOptions, LangConverter

from . import models
from . import views as tourism_views

register_converter(LangConverter, 'lang')

app_name = 'tourism'
urlpatterns = [
    re_path(r'^api/(?P<lang>[a-z]{2}(-[a-z]{2,4})?)/treks/(?P<pk>\d+)/information_desks.geojson$', tourism_views.TrekInformationDeskViewSet.as_view({'get': 'list'}), name="trek_information_desk_geojson"),
    path('popup/add/organizer/', tourism_views.TouristicEventOrganizerCreatePopup.as_view(), name='organizer_add'),
]


class TouristicContentEntityOptions(PublishableEntityOptions):
    document_public_view = tourism_views.TouristicContentDocumentPublic
    document_public_booklet_view = tourism_views.TouristicContentDocumentBookletPublic
    markup_public_view = tourism_views.TouristicContentMarkupPublic


class TouristicEventEntityOptions(PublishableEntityOptions):
    document_public_view = tourism_views.TouristicEventDocumentPublic
    document_public_booklet_view = tourism_views.TouristicEventDocumentBookletPublic
    markup_public_view = tourism_views.TouristicEventMarkupPublic


if settings.TOURISM_ENABLED:
    urlpatterns += registry.register(models.TouristicEvent, TouristicEventEntityOptions,
                                     menu=settings.TOURISTICEVENT_MODEL_ENABLED)
    urlpatterns += registry.register(models.TouristicContent, TouristicContentEntityOptions,
                                     menu=settings.TOURISTICCONTENT_MODEL_ENABLED)
