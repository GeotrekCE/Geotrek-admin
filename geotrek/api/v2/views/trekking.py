from django.conf import settings
from django.db.models import F
from django.db.models.aggregates import Count
from django.http import Http404
from django.shortcuts import get_object_or_404

from rest_framework.response import Response
from functools import reduce

from geotrek.api.v2 import serializers as api_serializers, \
    viewsets as api_viewsets, filters as api_filters
from geotrek.api.v2.functions import Transform, Length, Length3D
from geotrek.trekking import models as trekking_models


class TrekViewSet(api_viewsets.GeotrekGeometricViewset):
    filter_backends = api_viewsets.GeotrekGeometricViewset.filter_backends + (api_filters.GeotrekTrekQueryParamsFilter,)
    serializer_class = api_serializers.TrekSerializer
    queryset = trekking_models.Trek.objects.existing() \
        .select_related('topo_object') \
        .prefetch_related('topo_object__aggregations', 'accessibilities', 'attachments') \
        .annotate(geom3d_transformed=Transform(F('geom_3d'), settings.API_SRID),
                  length_2d_m=Length('geom'),
                  length_3d_m=Length3D('geom_3d')) \
        .order_by('pk')  # Required for reliable pagination

    def retrieve(self, request, pk=None):
        # Return detail view even for unpublished treks that are childrens of other published treks
        qs = self.queryset
        trek = get_object_or_404(qs, pk=pk)
        list_status = self.parents_status([trek])
        if not reduce(lambda a, b: a or b, list_status, False):
            # return 404 if no ancestor is published
            raise Http404('No %s matches the given query.' % qs.model._meta.object_name)
        serializer = api_serializers.TrekSerializer(trek, many=False, context={'request': request})
        return Response(serializer.data)

    def parents_status(self, parents):
        """ Recursive function to check if ancestors of trek are published or not """
        status = []
        for trek in parents:
            status.append(trek.published)
            status = status + self.parents_status(trek.parents)
        return status


class TourViewSet(TrekViewSet):
    serializer_class = api_serializers.TourSerializer
    queryset = TrekViewSet.queryset.annotate(count_children=Count('trek_children')) \
        .filter(count_children__gt=0)


class PracticeViewSet(api_viewsets.GeotrekViewSet):
    filter_backends = api_viewsets.GeotrekViewSet.filter_backends + (api_filters.GeotrekRelatedPortalTrekFilter,)
    serializer_class = api_serializers.PracticeSerializer
    queryset = trekking_models.Practice.objects.all()


class NetworksViewSet(api_viewsets.GeotrekViewSet):
    filter_backends = api_viewsets.GeotrekViewSet.filter_backends + (api_filters.GeotrekRelatedPortalTrekFilter,)
    serializer_class = api_serializers.NetworkSerializer
    queryset = trekking_models.TrekNetwork.objects.all()


class DifficultyViewSet(api_viewsets.GeotrekViewSet):
    filter_backends = api_viewsets.GeotrekViewSet.filter_backends + (api_filters.GeotrekRelatedPortalTrekFilter,)
    serializer_class = api_serializers.TrekDifficultySerializer
    queryset = trekking_models.DifficultyLevel.objects.all()


class POIViewSet(api_viewsets.GeotrekGeometricViewset):
    filter_backends = api_viewsets.GeotrekGeometricViewset.filter_backends + (api_filters.GeotrekPOIFilter,)
    serializer_class = api_serializers.POISerializer
    queryset = trekking_models.POI.objects.existing() \
        .select_related('topo_object', 'type', ) \
        .prefetch_related('topo_object__aggregations', 'attachments') \
        .annotate(geom3d_transformed=Transform(F('geom_3d'), settings.API_SRID)) \
        .order_by('pk')  # Required for reliable pagination


class POITypeViewSet(api_viewsets.GeotrekViewSet):
    serializer_class = api_serializers.POITypeSerializer
    queryset = trekking_models.POIType.objects.all()


class AccessibilityViewSet(api_viewsets.GeotrekViewSet):
    filter_backends = api_viewsets.GeotrekViewSet.filter_backends + (api_filters.GeotrekRelatedPortalTrekFilter,)
    serializer_class = api_serializers.AccessibilitySerializer
    queryset = trekking_models.Accessibility.objects.all()


class RouteViewSet(api_viewsets.GeotrekViewSet):
    filter_backends = api_viewsets.GeotrekViewSet.filter_backends + (api_filters.GeotrekRelatedPortalTrekFilter,)
    serializer_class = api_serializers.RouteSerializer
    queryset = trekking_models.Route.objects.all()
