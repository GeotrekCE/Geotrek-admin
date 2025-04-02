from geotrek.api.v2 import serializers as api_serializers
from geotrek.api.v2 import viewsets as api_viewsets
from geotrek.zoning import models as zoning_models


class CityViewSet(api_viewsets.GeotrekGeometricViewset):
    serializer_class = api_serializers.CitySerializer
    queryset = zoning_models.City.objects.all()


class DistrictViewSet(api_viewsets.GeotrekGeometricViewset):
    serializer_class = api_serializers.DistrictsSerializer
    queryset = zoning_models.District.objects.all()
