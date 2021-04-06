from geotrek.api.v2 import serializers as api_serializers, viewsets as api_viewsets, filters as api_filters
from geotrek.api.v2.utils import filter_queryset_related_objects_published
from geotrek.common import models as common_models


class TargetPortalViewSet(api_viewsets.GeotrekViewSet):
    serializer_class = api_serializers.TargetPortalSerializer
    queryset = common_models.TargetPortal.objects.all()


class ThemeViewSet(api_viewsets.GeotrekViewSet):
    filter_backends = api_viewsets.GeotrekViewSet.filter_backends + (api_filters.GeotrekRelatedPortalTrekFilter,)
    serializer_class = api_serializers.ThemeSerializer

    def get_queryset(self):
        qs = common_models.Theme.objects.all()
        return filter_queryset_related_objects_published(qs, self.request, 'treks')


class SourceViewSet(api_viewsets.GeotrekViewSet):
    filter_backends = api_viewsets.GeotrekViewSet.filter_backends + (api_filters.GeotrekRelatedPortalTrekFilter,)
    serializer_class = api_serializers.RecordSourceSerializer

    def get_queryset(self):
        qs = common_models.RecordSource.objects.all()
        return filter_queryset_related_objects_published(qs, self.request, 'treks')


class ReservationSystemViewSet(api_viewsets.GeotrekViewSet):
    filter_backends = api_viewsets.GeotrekViewSet.filter_backends + (api_filters.GeotrekRelatedPortalReservationSystemFilter,)
    serializer_class = api_serializers.ReservationSystemSerializer

    def get_queryset(self):
        qs = common_models.ReservationSystem.objects.all()
        return filter_queryset_related_objects_published(qs, self.request, 'touristiccontent')


class LabelViewSet(api_viewsets.GeotrekViewSet):
    filter_backends = api_viewsets.GeotrekViewSet.filter_backends + (api_filters.GeotrekRelatedPortalTrekFilter,)
    serializer_class = api_serializers.LabelSerializer

    def get_queryset(self):
        qs = common_models.Label.objects.all()
        return filter_queryset_related_objects_published(qs, self.request, 'treks')
