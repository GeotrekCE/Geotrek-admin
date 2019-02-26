from __future__ import unicode_literals

from django_filters.rest_framework.backends import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from geotrek.api.v2 import filters as api_filters
from geotrek.api.mobile import pagination as api_pagination_mobile
from geotrek.api.mobile.serializers.common import override_serializer


class GeotrekViewset(viewsets.ReadOnlyModelViewSet):
    filter_backends = (DjangoFilterBackend,
                       api_filters.GeotrekQueryParamsFilter,
                       api_filters.GeotrekInBBoxFilter,
                       api_filters.GeotrekDistanceToPointFilter,
                       api_filters.GeotrekPublishedFilter)
    distance_filter_field = 'geometry'
    distance_filter_convert_meters = True
    pagination_class = api_pagination_mobile.StandardMobileSetPagination
    permission_classes = [IsAuthenticatedOrReadOnly, ]
    authentication_classes = [BasicAuthentication, SessionAuthentication]

    def get_serializer_class(self):
        base_serializer_class = super(GeotrekViewset, self).get_serializer_class()
        format_output = self.request.query_params.get('format', 'json')
        return override_serializer(format_output, base_serializer_class)

    def get_serializer_context(self):
        return {
            'request': self.request,
            'kwargs': self.kwargs
        }
