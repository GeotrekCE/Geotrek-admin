from datetime import datetime

from django.conf import settings
from django.contrib.gis.db.models.functions import Transform
from django.db.models import F, Q

from geotrek.api.v2 import filters as api_filters
from geotrek.api.v2 import serializers as api_serializers
from geotrek.api.v2 import viewsets as api_viewsets
from geotrek.zoning import models as zoning_models


class CityViewSet(api_viewsets.GeotrekGeometricViewset):
    serializer_class = api_serializers.CitySerializer
    queryset = zoning_models.City.objects.all()


class DistrictViewSet(api_viewsets.GeotrekGeometricViewset):
    serializer_class = api_serializers.DistrictsSerializer
    queryset = zoning_models.District.objects.all()


class VigilanceAreaViewSet(api_viewsets.GeotrekGeometricViewset):
    serializer_class = api_serializers.VigilanceAreaSerializer
    filter_backends = (
        *api_viewsets.GeotrekGeometricViewset.filter_backends,
        api_filters.UpdateOrCreateDateFilter,
        api_filters.GeotrekVigilanceAreaFilter,
    )

    def get_queryset(self):
        qs = (
            zoning_models.VigilanceArea.objects.filter(published=True)
            .annotate(geom_transformed=Transform(F("geom"), settings.API_SRID))
            .filter(Q(end_date__isnull=True) | Q(end_date__gte=datetime.now()))
            .select_related("vigilance_area_type")
            .prefetch_related("portals", "sources")
        )
        return qs


class VigilanceAreaTypeViewSet(api_viewsets.GeotrekViewSet):
    serializer_class = api_serializers.VigilanceAreaTypeSerializer
    queryset = zoning_models.VigilanceAreaType.objects.all().order_by("pk")
