from django.http import Http404
from django.views.decorators.cache import cache_page
from django.conf import settings
from django.utils.decorators import method_decorator
from djgeojson.views import GeoJSONLayerView

from .models import City, RestrictedArea, RestrictedAreaType, District


class LandLayerMixin(object):
    srid = settings.API_SRID
    precision = settings.LAYER_PRECISION_LAND
    simplify = settings.LAYER_SIMPLIFY_LAND

    @method_decorator(cache_page(settings.CACHE_TIMEOUT_LAND_LAYERS, cache="fat"))
    def dispatch(self, request, *args, **kwargs):
        return super(LandLayerMixin, self).dispatch(request, *args, **kwargs)


class CityGeoJSONLayer(LandLayerMixin, GeoJSONLayerView):
    model = City


class RestrictedAreaGeoJSONLayer(LandLayerMixin, GeoJSONLayerView):
    model = RestrictedArea


class RestrictedAreaTypeGeoJSONLayer(LandLayerMixin, GeoJSONLayerView):
    model = RestrictedArea

    def get_queryset(self):
        type_pk = self.kwargs['type_pk']
        qs = super(RestrictedAreaTypeGeoJSONLayer, self).get_queryset()
        try:
            RestrictedAreaType.objects.get(pk=type_pk)
        except RestrictedAreaType.DoesNotExist:
            raise Http404
        return qs.filter(area_type=type_pk)


class DistrictGeoJSONLayer(LandLayerMixin, GeoJSONLayerView):
    model = District
    properties = ['name']
