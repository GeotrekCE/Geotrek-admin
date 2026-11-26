from rest_framework.permissions import IsAuthenticated

from geotrek.api.v2 import filters as api_filters
from geotrek.api.v2 import serializers as api_serializers
from geotrek.api.v2 import viewsets as api_viewsets
from geotrek.api.v2.utils import annotate_geojson
from geotrek.core import models as core_models


class PathViewSet(api_viewsets.GeotrekGeometricViewset):
    """
    Use HTTP basic authentication to access this endpoint.
    """

    filter_backends = (
        *api_viewsets.GeotrekGeometricViewset.filter_backends,
        api_filters.UpdateOrCreateDateFilter,
    )
    permission_classes = [IsAuthenticated]
    serializer_class = api_serializers.PathSerializer

    def get_queryset(self):
        include_bbox = self.request.query_params.get("format") == "geojson"
        queryset = (
            core_models.Path.objects.select_related("comfort", "source", "stake")
            .prefetch_related("usages", "networks")
            .defer("geom", "geom_3d")
            .order_by("pk")
        )  # Required for reliable pagination
        return annotate_geojson(
            queryset, field_name="geom_3d", include_bbox=include_bbox
        )
