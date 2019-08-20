from django.conf import settings
from django.conf.urls import url

from mapentity.registry import registry

from geotrek.common.urls import PublishableEntityOptions

from . import models
from .views import DiveMapImage


urlpatterns = [
    url(r'^image/dive-(?P<pk>\d+)-(?P<lang>\w\w).png$', DiveMapImage.as_view(), name='dive_map_image'),
]


class DiveEntityOptions(PublishableEntityOptions):
    # document_public_view = DiveDocumentPublic
    # markup_public_view = DiveMarkupPublic

    # def get_serializer(self):
    #     return diving_serializers.DiveSerializer

    def get_queryset(self):
        return self.model.objects.existing()


urlpatterns += registry.register(models.Dive, DiveEntityOptions, menu=settings.DIVE_MODEL_ENABLED)
