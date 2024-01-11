from django.conf import settings
from django.urls import path, register_converter

from mapentity.registry import registry
from rest_framework.routers import DefaultRouter

from geotrek.common.urls import PublishableEntityOptions, LangConverter

from . import models
from .views import (DiveMapImage, DivePOIViewSet, DiveServiceViewSet, DiveAPIViewSet,
                    DiveDocumentBookletPublic, DiveDocumentPublic, DiveMarkupPublic)

register_converter(LangConverter, 'lang')

app_name = 'diving'
urlpatterns = [
    path('image/dive-<int:pk>-<lang:lang>.png', DiveMapImage.as_view(), name='dive_map_image'),
    path('api/<lang:lang>/dives/<int:pk>/pois.geojson', DivePOIViewSet.as_view({'get': 'list'}),
         name="dive_poi_geojson"),
    path('api/<lang:lang>/dives/<int:pk>/services.geojson', DiveServiceViewSet.as_view({'get': 'list'}),
         name="dive_service_geojson"),
]


class DiveEntityOptions(PublishableEntityOptions):
    document_public_booklet_view = DiveDocumentBookletPublic
    document_public_view = DiveDocumentPublic
    markup_public_view = DiveMarkupPublic

    def get_queryset(self):
        return self.model.objects.existing()


router = DefaultRouter(trailing_slash=False)


router.register(r'^api/(?P<lang>[a-z]{2}(-[a-z]{2,4})?)/dives', DiveAPIViewSet, basename='dive')
urlpatterns += router.urls

urlpatterns += registry.register(models.Dive, DiveEntityOptions, menu=settings.DIVE_MODEL_ENABLED)
