from django.conf import settings
from django.conf.urls import url

from mapentity.registry import registry

from geotrek.common.urls import PublishableEntityOptions

from . import models
from .views import DiveMapImage, DivePOIViewSet, DiveServiceViewSet


urlpatterns = [
    url(r'^image/dive-(?P<pk>\d+)-(?P<lang>\w\w).png$', DiveMapImage.as_view(), name='dive_map_image'),
    url(r'^api/(?P<lang>\w\w)/dives/(?P<pk>\d+)/pois\.geojson$', DivePOIViewSet.as_view({'get': 'list'}),
        name="dive_poi_geojson"),
    url(r'^api/(?P<lang>\w\w)/dives/(?P<pk>\d+)/services\.geojson$', DiveServiceViewSet.as_view({'get': 'list'}),
        name="dive_service_geojson"),
]


class DiveEntityOptions(PublishableEntityOptions):
    # document_public_view = DiveDocumentPublic
    # markup_public_view = DiveMarkupPublic

    # def get_serializer(self):
    #     return diving_serializers.DiveSerializer

    def get_queryset(self):
        return self.model.objects.existing()


urlpatterns += registry.register(models.Dive, DiveEntityOptions, menu=settings.DIVE_MODEL_ENABLED)
