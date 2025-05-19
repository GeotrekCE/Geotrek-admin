from django.conf import settings
from django.contrib.gis.db.models.functions import Transform
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import permissions
from rest_framework.generics import ListAPIView

from ..common.functions import SimplifyPreserveTopology
from .models import City, District, RestrictedArea, RestrictedAreaType
from .serializers import CitySerializer, DistrictSerializer, RestrictedAreaSerializer


class LandGeoJSONAPIViewMixin(ListAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.model.objects.annotate(
            api_geom=Transform(
                SimplifyPreserveTopology("geom", settings.LAYER_SIMPLIFY_LAND),
                settings.API_SRID,
            )
        ).defer("name", "geom")

    @method_decorator(
        cache_page(
            settings.CACHE_TIMEOUT_LAND_LAYERS,
            cache=settings.MAPENTITY_CONFIG["GEOJSON_LAYERS_CACHE_BACKEND"],
        )
    )
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class CityGeoJSONAPIView(LandGeoJSONAPIViewMixin):
    model = City
    serializer_class = CitySerializer


class RestrictedAreaGeoJSONAPIView(LandGeoJSONAPIViewMixin):
    model = RestrictedArea
    serializer_class = RestrictedAreaSerializer


class RestrictedAreaTypeGeoJSONLayer(RestrictedAreaGeoJSONAPIView):
    model = RestrictedArea

    def get_queryset(self):
        type_pk = self.kwargs["type_pk"]
        qs = super().get_queryset()
        get_object_or_404(RestrictedAreaType, pk=type_pk)
        return qs.filter(area_type=type_pk)


class DistrictGeoJSONAPIView(LandGeoJSONAPIViewMixin):
    model = District
    serializer_class = DistrictSerializer
