from django.conf import settings
from django.conf.urls import patterns, url

from mapentity import registry

from geotrek.common.urls import PublishableEntityOptions

from . import models
from . import views as tourism_views
from . import serializers as tourism_serializers


urlpatterns = patterns(
    '',
    url(r'^api/(?P<lang>\w\w)/information_desks.(?P<format>geojson)$', tourism_views.InformationDeskViewSet.as_view({'get': 'list'}), name="information_desk_geojson"),
    url(r'^api/(?P<lang>\w\w)/information_desks-(?P<type>\d+).(?P<format>geojson)$', tourism_views.InformationDeskViewSet.as_view({'get': 'list'})),
    url(r'^api/treks/(?P<pk>\d+)/information_desks.(?P<format>geojson)$', tourism_views.TrekInformationDeskViewSet.as_view({'get': 'list'}), name="trek_information_desk_geojson"),
    url(r'^api/(?P<lang>\w\w)/treks/(?P<pk>\d+)/touristicevents\.(?P<format>geojson)$', tourism_views.TrekTouristicEventViewSet.as_view({'get': 'list'}), name="trek_events_geojson"),
    url(r'^api/(?P<lang>\w\w)/treks/(?P<pk>\d+)/touristiccontents\.(?P<format>geojson)$', tourism_views.TrekTouristicContentViewSet.as_view({'get': 'list'}), name="trek_contents_geojson"),
    url(r'^api/(?P<lang>\w\w)/touristiccategories\.json$', tourism_views.TouristicCategoryView.as_view(), name="touristic_categories_json"),
)


class TouristicContentEntityOptions(PublishableEntityOptions):
    document_public_view = tourism_views.TouristicContentDocumentPublic

    def get_serializer(self):
        return tourism_serializers.TouristicContentSerializer

    def get_queryset(self):
        return self.model.objects.existing()


if settings.TOURISM_ENABLED:
    urlpatterns += registry.register(models.TouristicContent, TouristicContentEntityOptions)


class TouristicEventEntityOptions(PublishableEntityOptions):
    document_public_view = tourism_views.TouristicEventDocumentPublic

    def get_serializer(self):
        return tourism_serializers.TouristicEventSerializer

    def get_queryset(self):
        return self.model.objects.existing()


if settings.TOURISM_ENABLED:
    urlpatterns += registry.register(models.TouristicEvent, TouristicEventEntityOptions)
