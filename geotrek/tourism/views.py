import json

import requests
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from tif2geojson import tif2geojson
from mapentity.views import JSONResponseMixin

from geotrek.tourism.models import DataSource, DATA_SOURCE_TYPES


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
                'pictogram': ds.pictogram or '',
            })
        return results

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(DataSourceList, self).dispatch(*args, **kwargs)


class DataSourceGeoJSON(JSONResponseMixin, DetailView):
    model = DataSource

    def get_context_data(self, *args, **kwargs):
        source = self.get_object()
        response = requests.get(source.url)
        if source.type == DATA_SOURCE_TYPES.GEOJSON:
            geojson = json.loads(response.text)
        elif source.type == DATA_SOURCE_TYPES.TOURINFRANCE:
            geojson = tif2geojson(response.text)
        else:
            raise NotImplementedError
        return geojson

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(DataSourceGeoJSON, self).dispatch(*args, **kwargs)
