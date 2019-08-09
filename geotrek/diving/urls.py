from django.conf import settings

from mapentity.registry import registry

from geotrek.common.urls import PublishableEntityOptions

from . import models


urlpatterns = [
]


class DiveEntityOptions(PublishableEntityOptions):
    # document_public_view = DiveDocumentPublic
    # markup_public_view = DiveMarkupPublic

    # def get_serializer(self):
    #     return diving_serializers.DiveSerializer

    def get_queryset(self):
        return self.model.objects.existing()


urlpatterns += registry.register(models.Dive, DiveEntityOptions, menu=settings.DIVE_MODEL_ENABLED)
