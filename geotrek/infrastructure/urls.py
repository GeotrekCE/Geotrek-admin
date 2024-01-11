from django.conf import settings
from django.urls import path, register_converter

from mapentity.registry import registry
from rest_framework.routers import DefaultRouter

from . import models
from geotrek.trekking.views import TrekInfrastructureViewSet
from geotrek.common.urls import LangConverter
from .views import InfrastructureAPIViewSet

register_converter(LangConverter, 'lang')

app_name = 'infrastructure'

urlpatterns = registry.register(models.Infrastructure, menu=settings.INFRASTRUCTURE_MODEL_ENABLED)

router = DefaultRouter(trailing_slash=False)


router.register(r'^api/(?P<lang>[a-z]{2}(-[a-z]{2,4})?)/infrastructures', InfrastructureAPIViewSet, basename='infrastructrure')
urlpatterns += router.urls

urlpatterns += [
    path('api/<lang:lang>/treks/<int:pk>/infrastructures.geojson',
         TrekInfrastructureViewSet.as_view({'get': 'list'}), name="trek_infrastructure_geojson"),
]
