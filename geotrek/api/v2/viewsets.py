from __future__ import unicode_literals

from django_filters.rest_framework.backends import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework_extensions.mixins import DetailSerializerMixin

from geotrek.api.v2 import pagination as api_pagination, filters as api_filters
from geotrek.api.v2.serializers import override_serializer


class GeotrekViewset(DetailSerializerMixin, viewsets.ReadOnlyModelViewSet):
    filter_backends = (DjangoFilterBackend,
                       api_filters.GeotrekQueryParamsFilter,
                       api_filters.GeotrekInBBoxFilter,
                       api_filters.GeotrekDistanceToPointFilter,
                       api_filters.GeotrekPublishedFilter)
    distance_filter_field = 'geometry'
    distance_filter_convert_meters = True
    pagination_class = api_pagination.StandardResultsSetPagination
    permission_classes = [IsAuthenticated, ]
    authentication_classes = [BasicAuthentication, SessionAuthentication]

    def get_serializer_class(self):
        base_serializer_class = super(GeotrekViewset, self).get_serializer_class()
        format_output = self.request.query_params.get('format', 'json')
        dimension = self.request.query_params.get('dim', '2')
        return override_serializer(format_output, dimension, base_serializer_class)

    def get_serializer_context(self):
        return {
            'request': self.request,
            'kwargs': self.kwargs
        }
