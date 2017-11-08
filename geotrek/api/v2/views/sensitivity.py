from __future__ import unicode_literals

from django.conf import settings

from geotrek.api.v2 import serializers as api_serializers, \
    viewsets as api_viewsets
from geotrek.api.v2.functions import Transform
from geotrek.sensitivity import models as sensitivity_models


class SensitiveAreaViewSet(api_viewsets.GeotrekViewset):
    serializer_class = api_serializers.SensitiveAreaListSerializer
    serializer_detail_class = api_serializers.SensitiveAreaDetailSerializer
    queryset = sensitivity_models.SensitiveArea.objects.existing() \
        .prefetch_related('species') \
        .annotate(geom2d_transformed=Transform('geom', settings.API_SRID))
