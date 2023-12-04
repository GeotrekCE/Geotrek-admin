from hashlib import md5

from django.conf import settings
from django_filters.rest_framework.backends import DjangoFilterBackend
from mapentity.renderers import GeoJSONRenderer
from rest_framework import viewsets, renderers
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated

from geotrek.api.v2 import pagination as api_pagination, filters as api_filters
from geotrek.api.v2.cache import RetrieveCacheResponseMixin
from geotrek.api.v2.serializers import override_serializer


class GeotrekViewSet(RetrieveCacheResponseMixin, viewsets.ReadOnlyModelViewSet):
    filter_backends = (
        DjangoFilterBackend,
        api_filters.GeotrekQueryParamsFilter,
        api_filters.GeotrekPublishedFilter,
    )
    pagination_class = api_pagination.StandardResultsSetPagination
    permission_classes = [IsAuthenticatedOrReadOnly, ] if settings.API_IS_PUBLIC else [IsAuthenticated, ]
    authentication_classes = [BasicAuthentication, SessionAuthentication]
    renderer_classes = [renderers.JSONRenderer, renderers.BrowsableAPIRenderer, ] if settings.DEBUG else [renderers.JSONRenderer, ]
    lookup_value_regex = r'\d+'

    def get_ordered_query_params(self):
        """ Get multi value query params sorted by key """
        parameters = self.request.query_params
        sorted_keys = sorted(parameters.keys())
        return {k: sorted(parameters.getlist(k)) for k in sorted_keys}

    def get_base_cache_string(self):
        """ return cache string as url path + ordered query params """
        proto_scheme = self.request.headers.get('X-Forwarded-Proto', self.request.scheme)  # take care about scheme defined in nginx.conf
        return f"{self.request.path}:{self.get_ordered_query_params()}:{self.request.accepted_renderer.format}:{proto_scheme}"

    def get_object_cache_key(self, pk):
        """ return specific object cache key based on object date_update column"""
        # don't directly use get_object or get_queryset to avoid select / prefetch and annotation sql queries
        # insure object exists and doesn't raise exception
        instance = get_object_or_404(self.get_queryset().model, pk=pk)
        date_update = instance.date_update
        return f"{self.get_base_cache_string()}:{date_update.isoformat()}"

    def object_cache_key_func(self, **kwargs):
        """ cache key md5 for retrieve viewset action """
        return md5(self.get_object_cache_key(kwargs.get('kwargs').get('pk')).encode("utf-8")).hexdigest()

    def get_serializer_context(self):
        return {
            'request': self.request,
            'kwargs': self.kwargs
        }


class GeotrekGeometricViewset(GeotrekViewSet):
    filter_backends = GeotrekViewSet.filter_backends + (
        api_filters.GeotrekQueryParamsDimensionFilter,
        api_filters.GeotrekInBBoxFilter,
        api_filters.GeotrekDistanceToPointFilter,
    )
    distance_filter_field = 'geom'
    bbox_filter_field = 'geom'
    bbox_filter_include_overlapping = True
    renderer_classes = GeotrekViewSet.renderer_classes + [GeoJSONRenderer, ]

    def get_serializer_class(self):
        base_serializer_class = super().get_serializer_class()
        format_output = self.request.query_params.get('format', 'json')
        return override_serializer(format_output, base_serializer_class)
