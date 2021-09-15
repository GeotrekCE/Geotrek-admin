from django.shortcuts import get_object_or_404

from rest_framework.response import Response

from geotrek.api.v2 import serializers as api_serializers, viewsets as api_viewsets, filters as api_filters
from geotrek.common import models as common_models


class TargetPortalViewSet(api_viewsets.GeotrekViewSet):
    serializer_class = api_serializers.TargetPortalSerializer
    queryset = common_models.TargetPortal.objects.all()


class ThemeViewSet(api_viewsets.GeotrekViewSet):
    filter_backends = api_viewsets.GeotrekViewSet.filter_backends + (api_filters.TreksAndTourismRelatedPortalThemeFilter,)
    serializer_class = api_serializers.ThemeSerializer
    queryset = common_models.Theme.objects.all()

    def retrieve(self, request, pk=None, format=None):
        # Allow to retrieve objects even if not visible in list view
        elem = get_object_or_404(common_models.Theme, pk=pk)
        serializer = api_serializers.ThemeSerializer(elem, many=False, context={'request': request})
        return Response(serializer.data)


class SourceViewSet(api_viewsets.GeotrekViewSet):
    filter_backends = api_viewsets.GeotrekViewSet.filter_backends + (api_filters.TrekRelatedPortalFilter,)
    serializer_class = api_serializers.RecordSourceSerializer
    queryset = common_models.RecordSource.objects.all()

    def retrieve(self, request, pk=None, format=None):
        # Allow to retrieve objects even if not visible in list view
        elem = get_object_or_404(common_models.RecordSource, pk=pk)
        serializer = api_serializers.RecordSourceSerializer(elem, many=False, context={'request': request})
        return Response(serializer.data)


class ReservationSystemViewSet(api_viewsets.GeotrekViewSet):
    filter_backends = api_viewsets.GeotrekViewSet.filter_backends + (api_filters.RelatedPortalStructureOrReservationSystemFilter,)
    serializer_class = api_serializers.ReservationSystemSerializer
    queryset = common_models.ReservationSystem.objects.all()

    def retrieve(self, request, pk=None, format=None):
        # Allow to retrieve objects even if not visible in list view
        elem = get_object_or_404(common_models.ReservationSystem, pk=pk)
        serializer = api_serializers.ReservationSystemSerializer(elem, many=False, context={'request': request})
        return Response(serializer.data)


class LabelViewSet(api_viewsets.GeotrekViewSet):
    filter_backends = api_viewsets.GeotrekViewSet.filter_backends + (api_filters.TrekRelatedPortalFilter,)
    serializer_class = api_serializers.LabelSerializer
    queryset = common_models.Label.objects.all()

    def retrieve(self, request, pk=None, format=None):
        # Allow to retrieve objects even if not visible in list view
        elem = get_object_or_404(common_models.Label, pk=pk)
        serializer = api_serializers.LabelSerializer(elem, many=False, context={'request': request})
        return Response(serializer.data)


class OrganismViewSet(api_viewsets.GeotrekViewSet):
    serializer_class = api_serializers.OrganismSerializer
    queryset = common_models.Organism.objects.all()
