from __future__ import unicode_literals

from django_filters.rest_framework.backends import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework_extensions.mixins import DetailSerializerMixin

from geotrek.api.v2 import pagination as api_pagination,\
    serializers as api_serializers, filters as api_filters


class GeotrekViewset(DetailSerializerMixin, viewsets.ReadOnlyModelViewSet):
    filter_backends = (DjangoFilterBackend,
                       api_filters.GeotrekInBBoxFilter,
                       api_filters.GeotrekDistanceToPointFilter)
    distance_filter_field = 'geom'
    distance_filter_convert_meters = True
    pagination_class = api_pagination.StandardResultsSetPagination

    def get_serializer_class(self):
        base_serializer_class = super(GeotrekViewset, self).get_serializer_class()
        format_output = self.request.query_params.get('format', 'json')
        dimension = self.request.query_params.get('dim', '2')
        final_class = None

        if format_output == 'geojson':
            if dimension == '3':
                class GeneratedGeo3DSerializer(api_serializers.Base3DSerializer,
                                               api_serializers.BaseGeoJSONSerializer,
                                               base_serializer_class):
                    class Meta(api_serializers.BaseGeoJSONSerializer.Meta,
                               base_serializer_class.Meta):
                        pass
                final_class = GeneratedGeo3DSerializer

            else:
                class GeneratedGeoSerializer(api_serializers.BaseGeoJSONSerializer,
                                            base_serializer_class):
                    class Meta(api_serializers.BaseGeoJSONSerializer.Meta,
                                            base_serializer_class.Meta):
                        pass
                final_class = GeneratedGeoSerializer
        else:
            if dimension == '3':
                class Generated3DSerializer(api_serializers.Base3DSerializer,
                                           base_serializer_class):
                    class Meta(base_serializer_class.Meta):
                        pass
                final_class = Generated3DSerializer

            else:
                final_class = base_serializer_class

        return final_class
