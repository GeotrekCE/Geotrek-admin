from __future__ import unicode_literals

from django.conf import settings
from django.db.models import F, Case, When

from geotrek.api.v2 import serializers as api_serializers, \
    viewsets as api_viewsets
from geotrek.api.v2.functions import Transform, Buffer, GeometryType
from geotrek.sensitivity import models as sensitivity_models


class SensitiveAreaViewSet(api_viewsets.GeotrekViewset):
    serializer_class = api_serializers.SensitiveAreaListSerializer
    serializer_detail_class = api_serializers.SensitiveAreaDetailSerializer
    queryset = sensitivity_models.SensitiveArea.objects.existing() \
        .prefetch_related('species') \
        .annotate(geom_type=GeometryType(F('geom'))) \
        .annotate(geom2d_transformed=Case(
            When(geom_type='POINT', then=Buffer(Transform('geom', settings.API_SRID), F('species__radius'), 16)),
            defaut=Transform('geom', settings.API_SRID)
        ))

# .annotate(geom2d_transformed=Buffer(Transform('geom', settings.API_SRID), F('species__radius'), 16))
