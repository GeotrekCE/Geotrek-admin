from geotrek.api.v2 import serializers as api_serializers, viewsets as api_viewsets, filters as api_filters
from geotrek.common import models as common_models


class TargetPortalViewSet(api_viewsets.GeotrekViewSet):
    serializer_class = api_serializers.TargetPortalSerializer
    queryset = common_models.TargetPortal.objects.all()


class ThemeViewSet(api_viewsets.GeotrekViewSet):
    filter_backends = api_viewsets.GeotrekViewSet.filter_backends + (api_filters.GeotrekRelatedPortalTrekFilter,)
    serializer_class = api_serializers.ThemeSerializer
    queryset = common_models.Theme.objects.all()


class SourceViewSet(api_viewsets.GeotrekViewSet):
    filter_backends = api_viewsets.GeotrekViewSet.filter_backends + (api_filters.GeotrekRelatedPortalTrekFilter,)
    serializer_class = api_serializers.RecordSourceSerializer
    queryset = common_models.RecordSource.objects.all()


class ReservationSystemViewSet(api_viewsets.GeotrekViewSet):
    filter_backends = api_viewsets.GeotrekViewSet.filter_backends + (api_filters.GeotrekRelatedPortalReservationSystemFilter,)
    serializer_class = api_serializers.ReservationSystemSerializer
    queryset = common_models.ReservationSystem.objects.all()


class LabelViewSet(api_viewsets.GeotrekViewSet):
    filter_backends = api_viewsets.GeotrekViewSet.filter_backends + (api_filters.GeotrekRelatedPortalTrekFilter,)
    serializer_class = api_serializers.LabelSerializer
    queryset = common_models.Label.objects.all()
