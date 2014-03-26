from django.views.decorators.cache import cache_page
from django.conf import settings
from django.utils.decorators import method_decorator
from djgeojson.views import GeoJSONLayerView

from .models import City, RestrictedArea, District


class LandLayerMixin(object):
    srid = settings.API_SRID
    precision = settings.LAYER_PRECISION_LAND
    simplify = settings.LAYER_SIMPLIFY_LAND

    @method_decorator(cache_page(60 * 60 * 24, cache="fat"))
    def dispatch(self, request, *args, **kwargs):
        return super(LandLayerMixin, self).dispatch(request, *args, **kwargs)


class CityGeoJSONLayer(LandLayerMixin, GeoJSONLayerView):
    model = City


class RestrictedAreaGeoJSONLayer(LandLayerMixin, GeoJSONLayerView):
    model = RestrictedArea


class DistrictGeoJSONLayer(LandLayerMixin, GeoJSONLayerView):
    model = District
    properties = ['name']
