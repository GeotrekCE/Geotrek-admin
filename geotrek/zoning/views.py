from django.shortcuts import get_object_or_404
from django.views.decorators.cache import cache_page
from django.conf import settings
from django.utils.decorators import method_decorator
from djgeojson.views import GeoJSONLayerView

from mapentity.filters import MapEntityFilterSet
from .models import City, RestrictedArea, RestrictedAreaType, District


class LandLayerMixin(object):
    srid = settings.API_SRID
    precision = settings.LAYER_PRECISION_LAND
    simplify = settings.LAYER_SIMPLIFY_LAND

    @method_decorator(cache_page(settings.CACHE_TIMEOUT_LAND_LAYERS, cache="fat"))
    def dispatch(self, request, *args, **kwargs):
        return super(LandLayerMixin, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        # ensure mapentity filters are working for non Mapentity view
        qs = super().get_queryset()
        filtered = MapEntityFilterSet(self.request.GET, queryset=qs)
        return filtered.qs


class CityGeoJSONLayer(LandLayerMixin, GeoJSONLayerView):
    model = City


class RestrictedAreaGeoJSONLayer(LandLayerMixin, GeoJSONLayerView):
    model = RestrictedArea


class RestrictedAreaTypeGeoJSONLayer(LandLayerMixin, GeoJSONLayerView):
    model = RestrictedArea

    def get_queryset(self):
        type_pk = self.kwargs['type_pk']
        qs = super(RestrictedAreaTypeGeoJSONLayer, self).get_queryset()
        get_object_or_404(RestrictedAreaType, pk=type_pk)
        return qs.filter(area_type=type_pk)


class DistrictGeoJSONLayer(LandLayerMixin, GeoJSONLayerView):
    model = District
    properties = ['name']
