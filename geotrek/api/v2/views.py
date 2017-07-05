from __future__ import unicode_literals

from django.conf import settings
from django.db.models.aggregates import Count
from rest_framework import response, decorators
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny
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
    permission_classes = (AllowAny,)
    renderer_classes = [
        renderers.OpenAPIRenderer,
        renderers.SwaggerUIRenderer
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
    """
    A simple ViewSet for viewing accounts.
    """
    serializer_class = api_serializers.TouristicContentSerializer
    serializer_detail_class = api_serializers.TouristicContentDetailSerializer
    queryset = tourism_models.TouristicContent.objects.filter(deleted=False, published=True) \
        .select_related('category') \
        .transform(settings.API_SRID, field_name='geom')
    filter_fields = ('category', 'published')

    def get_serializer_class(self):
        """
        Obtain serializer switch List/Detail or GeoJSON / Simple JSON
        :return:
        """
        format = self.request.query_params.get('format', None)

        if self._is_request_to_detail_endpoint():
            if format == 'geojson':
                return api_serializers.TouristicContentGeoDetailSerializer

            else:
                return api_serializers.TouristicContentDetailSerializer
        else:
            if format == 'geojson':
                return api_serializers.TouristicContentGeoSerializer

            else:
                return api_serializers.TouristicContentSerializer


class TrekViewSet(api_viewsets.GeotrekViewset):
    serializer_class = api_serializers.TrekListSerializer
    serializer_detail_class = api_serializers.TrekDetailSerializer
    queryset = trekking_models.Trek.objects.filter(deleted=False) \
        .select_related('topo_object', 'difficulty') \
        .prefetch_related('topo_object__aggregations', 'themes', 'networks', 'attachments') \
        .annotate(geom2d_transformed=Transform('geom', settings.API_SRID),
                  geom3d_transformed=Transform('geom_3d', settings.API_SRID),
                  length_2d_m=Length('geom'),
                  length_3d_m=Length3D('geom_3d'))
    filter_fields = ('difficulty', 'published', 'themes', 'networks')

    @decorators.detail_route(methods=['get'])
    def touristiccontent(self, request, *args, **kwargs):
        instance = get_object_or_404(self.get_queryset(), pk=kwargs.get('pk'))
        qs = instance.touristic_contents
        qs = qs.prefetch_related('themes', )
        data = api_serializers.TouristicContentDetailSerializer(instance.touristic_contents,
                                                                many=True).data
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
