from __future__ import unicode_literals

from django.conf import settings
from django.db.models.aggregates import Count
from rest_framework import response, decorators, permissions
from rest_framework.schemas import SchemaGenerator
from rest_framework.views import APIView
from rest_framework_swagger import renderers

from geotrek.api.v2 import serializers as api_serializers, \
    viewsets as api_viewsets
from geotrek.api.v2.functions import Transform, Length, Length3D
from geotrek.core import models as core_models
from geotrek.trekking import models as trekking_models


class SwaggerSchemaView(APIView):
    permission_classes = (permissions.AllowAny,)
    renderer_classes = [
        renderers.OpenAPIRenderer,
        renderers.SwaggerUIRenderer,
    ]

    def get(self, request):
        generator = SchemaGenerator(
            title='Geotrek API v2 beta 1',
            urlconf='geotrek.api.v2.urls',
            url='/api/v2',
            description="New Geotrek OpenAPI. Please Authorize first."
        )
        schema = generator.get_schema(request=request)

        return response.Response(schema)


class PathViewSet(api_viewsets.GeotrekViewset):
    """
    Use HTTP basic authentication to access this endpoint.
    """
    serializer_class = api_serializers.PathListSerializer
    serializer_detail_class = api_serializers.PathListSerializer
    queryset = core_models.Path.objects.all() \
        .select_related('comfort', 'source', 'stake') \
        .prefetch_related('usages', 'networks') \
        .annotate(geom2d_transformed=Transform('geom', settings.API_SRID),
                  geom3d_transformed=Transform('geom_3d', settings.API_SRID),
                  length_2d_m=Length('geom'),
                  length_3d_m=Length3D('geom_3d'))


class TrekViewSet(api_viewsets.GeotrekViewset):
    serializer_class = api_serializers.TrekListSerializer
    serializer_detail_class = api_serializers.TrekDetailSerializer
    queryset = trekking_models.Trek.objects.existing() \
        .select_related('topo_object', 'difficulty', 'practice') \
        .prefetch_related('topo_object__aggregations', 'themes', 'networks', 'attachments') \
        .annotate(geom2d_transformed=Transform('geom', settings.API_SRID),
                  geom3d_transformed=Transform('geom_3d', settings.API_SRID),
                  length_2d_m=Length('geom'),
                  length_3d_m=Length3D('geom_3d'))
    filter_fields = ('difficulty', 'themes', 'networks', 'practice')

    @decorators.list_route(methods=['get'])
    def all_practices(self, request, *args, **kwargs):
        """
        Get all practices list
        """
        data = api_serializers.TrekPracticeSerializer(trekking_models.Practice.objects.all(),
                                                      many=True,
                                                      context={'request': request}).data
        return response.Response(data)

    @decorators.list_route(methods=['get'])
    def used_practices(self, request, *args, **kwargs):
        """
        Get practices used by Trek instances
        """
        data = api_serializers.TrekPracticeSerializer(trekking_models.Practice.objects.filter(
            pk__in=trekking_models.Trek.objects.existing().values_list('practice_id', flat=True)),
            many=True,
            context={'request': request}).data
        return response.Response(data)

    @decorators.list_route(methods=['get'])
    def all_themes(self, request, *args, **kwargs):
        """
        Get all themes list
        """
        data = api_serializers.TrekThemeSerializer(trekking_models.Theme.objects.all(),
                                                   many=True,
                                                   context={'request': request}).data
        return response.Response(data)

    @decorators.list_route(methods=['get'])
    def used_themes(self, request, *args, **kwargs):
        """
        Get themes used by Trek instances
        """
        data = api_serializers.TrekThemeSerializer(trekking_models.Theme.objects.filter(
            pk__in=trekking_models.Trek.objects.existing().values_list('themes', flat=True)),
            many=True,
            context={'request': request}).data
        return response.Response(data)

    @decorators.list_route(methods=['get'])
    def all_networks(self, request, *args, **kwargs):
        """
        Get all networks list
        """
        data = api_serializers.TrekNetworkSerializer(trekking_models.TrekNetwork.objects.all(),
                                                     many=True,
                                                     context={'request': request}).data
        return response.Response(data)

    @decorators.list_route(methods=['get'])
    def used_networks(self, request, *args, **kwargs):
        """
        Get networks used by Trek instances
        """
        data = api_serializers.TrekNetworkSerializer(trekking_models.TrekNetwork.objects.filter(
            pk__in=trekking_models.Trek.objects.existing().values_list('networks', flat=True)),
            many=True,
            context={'request': request}).data
        return response.Response(data)

    @decorators.list_route(methods=['get'])
    def all_difficulties(self, request, *args, **kwargs):
        """
        Get all difficulties list
        """
        qs = trekking_models.DifficultyLevel.objects.all()
        data = api_serializers.DifficultySerializer(qs, many=True, context={'request': request}).data
        return response.Response(data)

    @decorators.list_route(methods=['get'])
    def used_difficulties(self, request, *args, **kwargs):
        """
        Get difficulties used by Trek instances
        """
        data = api_serializers.DifficultySerializer(trekking_models.DifficultyLevel.objects.filter(
            pk__in=trekking_models.Trek.objects.existing().values_list('difficulty_id', flat=True)),
            many=True,
            context={'request': request}).data
        return response.Response(data)


class TourViewSet(TrekViewSet):
    serializer_class = api_serializers.TourListSerializer
    serializer_detail_class = api_serializers.TourDetailSerializer
    queryset = TrekViewSet.queryset.annotate(count_children=Count('trek_children')) \
        .filter(count_children__gt=0)


class POIViewSet(api_viewsets.GeotrekViewset):
    serializer_class = api_serializers.POIListSerializer
    serializer_detail_class = api_serializers.POIDetailSerializer
    queryset = trekking_models.POI.objects.existing() \
        .select_related('topo_object', 'type', ) \
        .prefetch_related('topo_object__aggregations', 'attachments') \
        .annotate(geom2d_transformed=Transform('geom', settings.API_SRID),
                  geom3d_transformed=Transform('geom_3d', settings.API_SRID))
    filter_fields = ('type',)

    @decorators.list_route(methods=['get'])
    def all_types(self, request, *args, **kwargs):
        """
        Get all POI types
        """
        data = api_serializers.POITypeSerializer(trekking_models.POIType.objects.all(),
                                                 many=True,
                                                 context={'request': request}).data
        return response.Response(data)

    @decorators.list_route(methods=['get'])
    def used_types(self, request, *args, **kwargs):
        """
        Get POI types used by POI instances
        """
        data = api_serializers.POITypeSerializer(
            trekking_models.POIType.objects.filter(pk__in=trekking_models.POI.objects.existing()
                                                   .values_list('type_id', flat=True)),
            many=True,
            context={'request': request}).data
        return response.Response(data)
