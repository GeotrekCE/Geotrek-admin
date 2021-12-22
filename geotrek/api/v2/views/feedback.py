from geotrek.api.v2 import serializers as api_serializers, viewsets as api_viewsets
from geotrek.feedback import models as feedback_models


class ReportStatusViewSet(api_viewsets.GeotrekViewSet):
    serializer_class = api_serializers.ReportStatusSerializer
    queryset = feedback_models.ReportStatus.objects \
        .order_by('pk')  # Required for reliable pagination


class ReportCategoryViewSet(api_viewsets.GeotrekViewSet):
    serializer_class = api_serializers.ReportCategorySerializer
    queryset = feedback_models.ReportCategory.objects \
        .order_by('pk')  # Required for reliable pagination


class ReportActivityViewSet(api_viewsets.GeotrekViewSet):
    serializer_class = api_serializers.ReportActivitySerializer
    queryset = feedback_models.ReportActivity.objects \
        .order_by('pk')  # Required for reliable pagination


class ReportProblemMagnitudeViewSet(api_viewsets.GeotrekViewSet):
    serializer_class = api_serializers.ReportProblemMagnitudeSerializer
    queryset = feedback_models.ReportProblemMagnitude.objects \
        .order_by('pk')  # Required for reliable pagination
