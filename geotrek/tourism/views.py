import logging

import requests
from requests.exceptions import RequestException
import geojson
from django.conf import settings
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.decorators.cache import cache_page
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from mapentity.views import JSONResponseMixin

from geotrek.tourism.models import DataSource
from .helpers import post_process

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
