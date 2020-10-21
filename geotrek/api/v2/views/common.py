from geotrek.api.v2 import serializers as api_serializers, \
    viewsets as api_viewsets
from geotrek.common import models as common_models


class TargetPortalViewSet(api_viewsets.GeotrekViewset):
    serializer_class = api_serializers.TargetPortalListSerializer
    serializer_detail_class = api_serializers.TargetPortalDetailSerializer
    queryset = common_models.TargetPortal.objects.all()
