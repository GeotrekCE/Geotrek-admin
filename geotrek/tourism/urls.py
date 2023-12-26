from django.conf import settings
from django.urls import path, re_path, register_converter

from mapentity.registry import registry
from rest_framework.routers import DefaultRouter

from geotrek.common.urls import PublishableEntityOptions, LangConverter

from . import models
from . import views as tourism_views
from .views import TouristicContentAPIViewSet, TouristicEventAPIViewSet

register_converter(LangConverter, 'lang')

app_name = 'tourism'
urlpatterns = [
    re_path(r'^api/(?P<lang>[a-z]{2}(-[a-z]{2,4})?)/information_desks.geojson$', tourism_views.InformationDeskViewSet.as_view({'get': 'list'}), name="information_desk_geojson"),
    re_path(r'^api/(?P<lang>[a-z]{2}(-[a-z]{2,4})?)/information_desks-(?P<type>\d+)\.geojson$', tourism_views.InformationDeskViewSet.as_view({'get': 'list'})),
    re_path(r'^api/(?P<lang>[a-z]{2}(-[a-z]{2,4})?)/treks/(?P<pk>\d+)/information_desks.geojson$', tourism_views.TrekInformationDeskViewSet.as_view({'get': 'list'}), name="trek_information_desk_geojson"),
    re_path(r'^api/(?P<lang>[a-z]{2}(-[a-z]{2,4})?)/treks/(?P<pk>\d+)/touristicevents\.geojson$', tourism_views.TrekTouristicEventViewSet.as_view({'get': 'list'}), name="trek_events_geojson"),
    re_path(r'^api/(?P<lang>[a-z]{2}(-[a-z]{2,4})?)/treks/(?P<pk>\d+)/touristiccontents\.geojson$', tourism_views.TrekTouristicContentViewSet.as_view({'get': 'list'}), name="trek_contents_geojson"),
    path('api/<lang:lang>/touristiccategories.json', tourism_views.TouristicCategoryView.as_view(), name="touristic_categories_json"),
    path('api/<lang:lang>/touristiccontents/<int:pk>/meta.html', tourism_views.TouristicContentMeta.as_view(), name="touristiccontent_meta"),
    path('api/<lang:lang>/touristicevents/<int:pk>/meta.html', tourism_views.TouristicEventMeta.as_view(), name="touristicevent_meta"),
]


class TouristicContentEntityOptions(PublishableEntityOptions):
    document_public_view = tourism_views.TouristicContentDocumentPublic
    document_public_booklet_view = tourism_views.TouristicContentDocumentBookletPublic
    markup_public_view = tourism_views.TouristicContentMarkupPublic


if settings.TOURISM_ENABLED:
    urlpatterns += registry.register(models.TouristicContent, TouristicContentEntityOptions,
                                     menu=settings.TOURISTICCONTENT_MODEL_ENABLED)


class TouristicEventEntityOptions(PublishableEntityOptions):
    document_public_view = tourism_views.TouristicEventDocumentPublic
    document_public_booklet_view = tourism_views.TouristicEventDocumentBookletPublic
    markup_public_view = tourism_views.TouristicEventMarkupPublic


router = DefaultRouter(trailing_slash=False)

router.register(r'^api/(?P<lang>[a-z]{2}(-[a-z]{2,4})?)/touristiccontents', TouristicContentAPIViewSet, basename='touristiccontent')
router.register(r'^api/(?P<lang>[a-z]{2}(-[a-z]{2,4})?)/touristicevents', TouristicEventAPIViewSet, basename='touristicevent')

urlpatterns += router.urls

if settings.TOURISM_ENABLED:
    urlpatterns += registry.register(models.TouristicEvent, TouristicEventEntityOptions,
                                     menu=settings.TOURISTICEVENT_MODEL_ENABLED)
