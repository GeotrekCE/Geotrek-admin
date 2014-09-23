import logging

import requests
from requests.exceptions import RequestException
import geojson
from djgeojson.views import GeoJSONLayerView
from django.conf import settings
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.decorators.cache import cache_page
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from mapentity.views import (JSONResponseMixin, MapEntityCreate,
                             MapEntityUpdate, MapEntityLayer, MapEntityList,
                             MapEntityDetail, MapEntityDelete)

from geotrek.authent.decorators import same_structure_required
from geotrek.tourism.models import DataSource, InformationDesk

from .forms import TouristicContentForm
from .helpers import post_process
from .models import TouristicContent


logger = logging.getLogger(__name__)


class DataSourceList(JSONResponseMixin, ListView):
    model = DataSource

    def get_context_data(self):
        results = []
        for ds in self.get_queryset():
            results.append({
                'id': ds.id,
                'title': ds.title,
                'url': ds.url,
                'type': ds.type,
                'pictogram_url': ds.pictogram.url,
                'geojson_url': ds.get_absolute_url(),
                'targets': ds.targets
            })
        return results

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(DataSourceList, self).dispatch(*args, **kwargs)


class DataSourceGeoJSON(JSONResponseMixin, DetailView):
    model = DataSource

    def get_context_data(self, *args, **kwargs):
        source = self.get_object()

        default_result = geojson.FeatureCollection(features=[])

        try:
            response = requests.get(source.url)
        except RequestException as e:
            logger.error(u"Source '%s' cannot be downloaded" % source.url)
            logger.exception(e)
            return default_result

        try:
            return post_process(source, self.request.LANGUAGE_CODE, response.text)
        except (ValueError, AssertionError) as e:
            return default_result

    @method_decorator(login_required)
    @method_decorator(cache_page(settings.CACHE_TIMEOUT_TOURISM_DATASOURCES, cache="fat"))
    def dispatch(self, *args, **kwargs):
        return super(DataSourceGeoJSON, self).dispatch(*args, **kwargs)


class InformationDeskGeoJSON(GeoJSONLayerView):
    model = InformationDesk
    srid = settings.API_SRID
    properties = {
        'id': 'id',
        'name': 'name',
        'description': 'description',
        'photo_url': 'photo_url',
        'phone': 'phone',
        'email': 'email',
        'website': 'website',
        'street': 'street',
        'postal_code': 'postal_code',
        'municipality': 'municipality',
        'latitude': 'latitude',
        'longitude': 'longitude',
        'serializable_type': 'type'
    }

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(InformationDeskGeoJSON, self).dispatch(*args, **kwargs)


class TouristicContentLayer(MapEntityLayer):
    queryset = TouristicContent.objects.existing()
    properties = ['name']


class TouristicContentList(MapEntityList):
    queryset = TouristicContent.objects.existing()
    columns = ['id', 'name']


class TouristicContentDetail(MapEntityDetail):
    queryset = TouristicContent.objects.existing()

    def context_data(self, *args, **kwargs):
        context = super(TouristicContentDetail, self).context_data(*args, **kwargs)
        context['can_edit'] = self.get_object().same_structure(self.request.user)
        return context


class TouristicContentCreate(MapEntityCreate):
    model = TouristicContent
    form_class = TouristicContentForm


class TouristicContentUpdate(MapEntityUpdate):
    queryset = TouristicContent.objects.existing()
    form_class = TouristicContentForm

    @same_structure_required('tourism:touristiccontent_detail')
    def dispatch(self, *args, **kwargs):
        return super(TouristicContentUpdate, self).dispatch(*args, **kwargs)


class TouristicContentDelete(MapEntityDelete):
    model = TouristicContent

    @same_structure_required('tourism:touristiccontent_detail')
    def dispatch(self, *args, **kwargs):
        return super(TouristicContentDelete, self).dispatch(*args, **kwargs)
