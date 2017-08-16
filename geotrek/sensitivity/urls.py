from django.conf import settings

from mapentity import registry

from geotrek.common.urls import PublishableEntityOptions

from . import models
from . import serializers as sensitivity_serializers


class SensitiveAreaEntityOptions(PublishableEntityOptions):
    def get_serializer(self):
        return sensitivity_serializers.SensitiveAreaSerializer

    def get_queryset(self):
        return self.model.objects.existing()


if settings.SENSITIVITY_ENABLED:
    urlpatterns = registry.register(models.SensitiveArea, SensitiveAreaEntityOptions)
else:
    urlpatterns = []
