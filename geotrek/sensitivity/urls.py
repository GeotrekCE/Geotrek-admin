from django.conf import settings
from django.urls import path, register_converter

from mapentity.registry import registry
from rest_framework.routers import DefaultRouter

from geotrek.common.urls import PublishableEntityOptions, LangConverter

from . import models
from . import serializers
from . import views


class SensitiveAreaEntityOptions(PublishableEntityOptions):
    def get_serializer(self):
        return serializers.SensitiveAreaSerializer

    def get_queryset(self):
        return self.model.objects.existing()


register_converter(LangConverter, 'lang')

app_name = 'sensitivity'
urlpatterns = [
    path('api/<lang:lang>/sensitiveareas/<int:pk>.kml',
         views.SensitiveAreaKMLDetail.as_view(), name="sensitivearea_kml_detail"),
    path('public/sensitiveareas/<int:pk>', views.SensitiveAreaPublicDetailView.as_view(), name="sensitivearea_public_detail")
]

router = DefaultRouter(trailing_slash=False)
router.register(r'^api/(?P<lang>[a-z]{2})/sensitiveareas', views.SensitiveAreaAPIViewSet, basename='sensitivearea')
urlpatterns += router.urls

if 'geotrek.trekking' in settings.INSTALLED_APPS:
    urlpatterns.append(path('api/<lang:lang>/treks/<int:pk>/sensitiveareas.geojson',
                            views.TrekSensitiveAreaViewSet.as_view({'get': 'list'}),
                            name="trek_sensitivearea_geojson"))
urlpatterns += registry.register(models.SensitiveArea, SensitiveAreaEntityOptions)
