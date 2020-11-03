from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from geotrek.api.v2 import serializers as api_serializers
from geotrek.common import models as common_models


class TargetPortalViewSet(ReadOnlyModelViewSet):
    serializer_class = api_serializers.TargetPortalListSerializer
    serializer_detail_class = api_serializers.TargetPortalDetailSerializer
    queryset = common_models.TargetPortal.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]


class ThemeViewSet(ReadOnlyModelViewSet):
    serializer_class = api_serializers.ThemeSerializer
    serializer_detail_class = api_serializers.ThemeSerializer
    queryset = common_models.Theme.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]
