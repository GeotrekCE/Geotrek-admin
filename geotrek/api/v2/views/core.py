from django.conf import settings
from django.db.models import F

from geotrek.api.v2 import serializers as api_serializers, \
    viewsets as api_viewsets
from geotrek.api.v2.functions import Transform, Length, Length3D
from geotrek.core import models as core_models


class PathViewSet(api_viewsets.GeotrekViewset):
    """
    Use HTTP basic authentication to access this endpoint.
    """
    serializer_class = api_serializers.PathListSerializer
    serializer_detail_class = api_serializers.PathListSerializer
    queryset = core_models.Path.objects.all() \
        .select_related('comfort', 'source', 'stake') \
        .prefetch_related('usages', 'networks') \
        .annotate(geom2d_transformed=Transform(F('geom'), settings.API_SRID),
                  geom3d_transformed=Transform(F('geom_3d'), settings.API_SRID),
                  length_2d_m=Length('geom'),
                  length_3d_m=Length3D('geom_3d')) \
        .order_by('pk')  # Required for reliable pagination
