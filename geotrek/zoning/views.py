from django.conf import settings
from django.contrib.gis.db.models.functions import Transform
from django.shortcuts import get_object_or_404
from mapentity.decorators import view_cache_latest, view_cache_response_content
from mapentity.renderers import GeoJSONRenderer
from rest_framework import permissions, viewsets

from ..common.functions import SimplifyPreserveTopology
from .models import City, District, RestrictedArea, RestrictedAreaType
from .serializers import CitySerializer, DistrictSerializer, RestrictedAreaSerializer


class LandGeoJSONAPIViewMixin:
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [GeoJSONRenderer]

    def get_queryset(self):
        return self.model.objects.annotate(
            api_geom=Transform(
                SimplifyPreserveTopology("geom", settings.LAYER_SIMPLIFY_LAND),
                settings.API_SRID,
            )
        ).defer("geom")

    @view_cache_latest()
    @view_cache_response_content()
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class RestrictedAreaViewSet(LandGeoJSONAPIViewMixin, viewsets.ReadOnlyModelViewSet):
    model = RestrictedArea
    serializer_class = RestrictedAreaSerializer

    def get_queryset(self):
        type_pk = self.kwargs.get("type_pk")
        qs = super().get_queryset()
        if type_pk:
            get_object_or_404(RestrictedAreaType, pk=type_pk)
            qs = qs.filter(area_type=type_pk)
        return qs


class DistrictViewSet(LandGeoJSONAPIViewMixin, viewsets.ReadOnlyModelViewSet):
    model = District
    serializer_class = DistrictSerializer


class CityViewSet(LandGeoJSONAPIViewMixin, viewsets.ReadOnlyModelViewSet):
    model = City
    serializer_class = CitySerializer
