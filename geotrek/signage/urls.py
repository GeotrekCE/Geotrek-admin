from django.conf import settings
from django.urls import path, register_converter

from mapentity.registry import registry
from rest_framework.routers import DefaultRouter

from . import models
from geotrek.trekking.views import TrekSignageViewSet
from geotrek.common.urls import LangConverter
from .views import SignageAPIViewSet, BladeAPIViewSet

register_converter(LangConverter, 'lang')

app_name = 'signage'
urlpatterns = registry.register(models.Signage, menu=settings.SIGNAGE_MODEL_ENABLED)

router = DefaultRouter(trailing_slash=False)


router.register(r'^api/(?P<lang>[a-z]{2}(-[a-z]{2,4})?)/signages', SignageAPIViewSet, basename='signage')

if settings.BLADE_ENABLED:
    urlpatterns += registry.register(models.Blade, menu=False)
    router.register(r'^api/(?P<lang>[a-z]{2}(-[a-z]{2,4})?)/blades', BladeAPIViewSet, basename='blade')

urlpatterns += router.urls

urlpatterns += [
    path('api/<lang:lang>/treks/<int:pk>/signages.geojson',
         TrekSignageViewSet.as_view({'get': 'list'}), name="trek_signage_geojson"),
]
