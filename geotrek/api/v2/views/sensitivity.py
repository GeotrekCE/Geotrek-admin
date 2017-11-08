from __future__ import unicode_literals

from django.conf import settings
from django.db.models import F, Case, When
from django_filters.rest_framework.backends import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from geotrek.api.v2 import serializers as api_serializers, \
    viewsets as api_viewsets
from geotrek.api.v2.functions import Transform, Buffer, GeometryType
from geotrek.sensitivity import models as sensitivity_models
from ..filters import GeotrekQueryParamsFilter, GeotrekInBBoxFilter, GeotrekSensitiveAreaFilter


class SensitiveAreaViewSet(api_viewsets.GeotrekViewset):
    filter_backends = (
        DjangoFilterBackend,
        GeotrekQueryParamsFilter,
        GeotrekInBBoxFilter,
        GeotrekSensitiveAreaFilter,
    )
    serializer_class = api_serializers.SensitiveAreaListSerializer
    serializer_detail_class = api_serializers.SensitiveAreaListSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    authentication_classes = []

    queryset = sensitivity_models.SensitiveArea.objects.existing() \
        .filter(published=True) \
        .prefetch_related('species') \
        .annotate(geom_type=GeometryType(F('geom'))) \
        .annotate(geom2d_transformed=Case(
            When(geom_type='POINT', then=Buffer(Transform('geom', settings.API_SRID), F('species__radius'), 16)),
            defaut=Transform('geom', settings.API_SRID)
        ))
