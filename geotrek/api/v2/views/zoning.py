from django_filters.rest_framework.backends import DjangoFilterBackend

from geotrek.api.v2 import filters as api_filters
from geotrek.api.v2 import serializers as api_serializers, \
    viewsets as api_viewsets
from geotrek.zoning import models as zoning_models


class CityViewSet(api_viewsets.GeotrekGeometricViewset):
    filter_backends = (DjangoFilterBackend,
                       api_filters.GeotrekQueryParamsFilter,
                       api_filters.GeotrekInBBoxFilter,
                       api_filters.GeotrekDistanceToPointFilter)
    serializer_class = api_serializers.CitySerializer
    queryset = zoning_models.City.objects.all()


class DistrictViewSet(api_viewsets.GeotrekGeometricViewset):
    filter_backends = (DjangoFilterBackend,
                       api_filters.GeotrekQueryParamsFilter,
                       api_filters.GeotrekQueryParamsDimensionFilter,
                       api_filters.GeotrekInBBoxFilter,
                       api_filters.GeotrekDistanceToPointFilter)
    serializer_class = api_serializers.DistrictsSerializer
    queryset = zoning_models.District.objects.all()
