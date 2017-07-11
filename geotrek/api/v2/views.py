from __future__ import unicode_literals

from django.conf import settings
from django.db.models.aggregates import Count
from rest_framework import response, decorators, permissions
from rest_framework.generics import get_object_or_404
from rest_framework.schemas import SchemaGenerator
from rest_framework.views import APIView
from rest_framework_swagger import renderers

from geotrek.api.v2 import serializers as api_serializers, \
    viewsets as api_viewsets
from geotrek.api.v2.functions import Transform, Length, Length3D
from geotrek.core import models as core_models
from geotrek.tourism import models as tourism_models
from geotrek.trekking import models as trekking_models


class SwaggerSchemaView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    renderer_classes = [
        renderers.OpenAPIRenderer,
        renderers.SwaggerUIRenderer,
    ]

    def get(self, request):
        generator = SchemaGenerator(
            title='Geotrek API v2',
            urlconf='geotrek.api.v2.urls',
            url='/apiv2'
        )
        schema = generator.get_schema(request=request, )

        return response.Response(schema)


class PathViewSet(api_viewsets.GeotrekViewset):
    serializer_class = api_serializers.PathListSerializer
    serializer_detail_class = api_serializers.PathListSerializer
    queryset = core_models.Path.objects.all() \
        .select_related('comfort', 'source', 'stake') \
        .prefetch_related('usages', 'networks') \
        .annotate(geom2d_transformed=Transform('geom', settings.API_SRID),
                  geom3d_transformed=Transform('geom_3d', settings.API_SRID),
                  length_2d_m=Length('geom'),
                  length_3d_m=Length3D('geom_3d'))


class TouristicContentViewSet(api_viewsets.GeotrekViewset):
    serializer_class = api_serializers.TouristicContentListSerializer
    serializer_detail_class = api_serializers.TouristicContentDetailSerializer
    queryset = tourism_models.TouristicContent.objects.filter(deleted=False, published=True) \
        .select_related('category') \
        .annotate(geom2d_transformed=Transform('geom', settings.API_SRID), )
    filter_fields = ('category', 'published')

    def get_serializer_class(self):
        format_output = self.request.query_params.get('format', 'json')
        # force 2D because 3D unavailable
        return api_serializers.override_serializer(format_output, '2', self.serializer_class)


class TrekViewSet(api_viewsets.GeotrekViewset):
    serializer_class = api_serializers.TrekListSerializer
    serializer_detail_class = api_serializers.TrekDetailSerializer
    queryset = trekking_models.Trek.objects.filter(deleted=False) \
        .select_related('topo_object', 'difficulty', 'practice') \
        .prefetch_related('topo_object__aggregations', 'themes', 'networks', 'attachments') \
        .annotate(geom2d_transformed=Transform('geom', settings.API_SRID),
                  geom3d_transformed=Transform('geom_3d', settings.API_SRID),
                  length_2d_m=Length('geom'),
                  length_3d_m=Length3D('geom_3d'))
    filter_fields = ('difficulty', 'published', 'themes', 'networks', 'practice')

    @decorators.list_route(methods=['get'])
    def practices(self, request, *args, **kwargs):
        """
        Get practice list
        """
        data = api_serializers.TrekPracticeSerializer(trekking_models.Practice.objects.all(),
                                                      many=True,
                                                      context={'request': request}).data
        return response.Response(data)

    @decorators.list_route(methods=['get'])
    def themes(self, request, *args, **kwargs):
        """
        Get theme list
        """
        data = api_serializers.TrekThemeSerializer(trekking_models.Theme.objects.all(),
                                                   many=True,
                                                   context={'request': request}).data
        return response.Response(data)

    @decorators.list_route(methods=['get'])
    def networks(self, request, *args, **kwargs):
        """
        Get network list
        """
        data = api_serializers.TrekNetworkSerializer(trekking_models.TrekNetwork.objects.all(),
                                                     many=True,
                                                     context={'request': request}).data
        return response.Response(data)

    @decorators.list_route(methods=['get'])
    def difficulties(self, request, *args, **kwargs):
        """
        Get network list
        """
        qs = trekking_models.DifficultyLevel.objects.all()
        data = api_serializers.DifficultySerializer(qs, many=True, context={'request': request}).data
        return response.Response(data)


class RoamingViewSet(TrekViewSet):
    serializer_class = api_serializers.RoamingListSerializer
    serializer_detail_class = api_serializers.RoamingDetailSerializer
    queryset = TrekViewSet.queryset.annotate(count_children=Count('trek_children')) \
        .filter(count_children__gt=0)


class POIViewSet(api_viewsets.GeotrekViewset):
    serializer_class = api_serializers.POIListSerializer
    serializer_detail_class = api_serializers.POIDetailSerializer
    queryset = trekking_models.POI.objects.filter(deleted=False) \
        .select_related('topo_object', 'type', ) \
        .prefetch_related('topo_object__aggregations', 'attachments') \
        .annotate(geom2d_transformed=Transform('geom', settings.API_SRID),
                  geom3d_transformed=Transform('geom_3d', settings.API_SRID))
    filter_fields = ('type', 'published')

    @decorators.list_route(methods=['get'])
    def alltypes(self, request, *args, **kwargs):
        """
        Get all POI types
        """
        data = api_serializers.POITypeSerializer(trekking_models.POIType.objects.all(),
                                                 many=True,
                                                 context={'request': request}).data
        return response.Response(data)
