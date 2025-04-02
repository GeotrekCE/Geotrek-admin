from django.conf import settings
from django.contrib.gis.db.models.functions import Transform
from django.db.models import F
from rest_framework.permissions import IsAuthenticated

from geotrek.api.v2 import filters as api_filters
from geotrek.api.v2 import serializers as api_serializers
from geotrek.api.v2 import viewsets as api_viewsets
from geotrek.api.v2.functions import Length3D
from geotrek.core import models as core_models


class PathViewSet(api_viewsets.GeotrekGeometricViewset):
    """
    Use HTTP basic authentication to access this endpoint.
    """

    filter_backends = api_viewsets.GeotrekGeometricViewset.filter_backends + (
        api_filters.UpdateOrCreateDateFilter,
    )
    permission_classes = [IsAuthenticated]
    serializer_class = api_serializers.PathSerializer

    def get_queryset(self):
        queryset = (
            core_models.Path.objects.select_related("comfort", "source", "stake")
            .prefetch_related("usages", "networks")
            .annotate(
                geom3d_transformed=Transform(F("geom_3d"), settings.API_SRID),
                length_3d_m=Length3D("geom_3d"),
            )
            .order_by("pk")
        )  # Required for reliable pagination
        return queryset
