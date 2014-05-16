# -*- coding: utf-8 -*-
import json
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import last_modified as cache_last_modified
from django.views.decorators.cache import never_cache as force_cache_validation
from django.views.generic.edit import BaseDetailView
from django.core.cache import get_cache
from django.shortcuts import redirect

from mapentity.views import (MapEntityLayer, MapEntityList, MapEntityJsonList,
                             MapEntityDetail, MapEntityDocument, MapEntityCreate, MapEntityUpdate,
                             MapEntityDelete, MapEntityFormat,
                             JSONResponseMixin, HttpJSONResponse, LastModifiedMixin)

from geotrek.authent.decorators import same_structure_required

from .models import Path, Trail
from .forms import PathForm
from .filters import PathFilter
from . import graph as graph_lib


@login_required
def last_list(request):
    last = request.session.get('last_list')  # set in MapEntityList
    if not last:
        return redirect('core:path_list')
    return redirect(last)

home = last_list


class HttpSVGResponse(HttpResponse):
    content_type = 'image/svg+xml'
    def __init__(self, content='', **kwargs):
        kwargs['content_type'] = self.content_type
        super(HttpSVGResponse, self).__init__(content, **kwargs)


class ElevationChart(LastModifiedMixin, BaseDetailView):

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ElevationChart, self).dispatch(*args, **kwargs)

    def render_to_response(self, context, **response_kwargs):
        return HttpSVGResponse(self.get_object().get_elevation_profile_svg(),
                               **response_kwargs)


class ElevationProfile(LastModifiedMixin, JSONResponseMixin, BaseDetailView):
    """Extract elevation profile from a path and return it as JSON"""

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ElevationProfile, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        """
        Put elevation profile into response context.
        """
        obj = self.get_object()
        data = {}
        # Formatted as distance, elevation, [lng, lat]
        for step in obj.get_elevation_profile():
            formatted = step[0], step[3], step[1:3]
            data.setdefault('profile', []).append(formatted)
        return data


class ElevationArea(LastModifiedMixin, JSONResponseMixin, BaseDetailView):
    """Extract elevation profile on an area and return it as JSON"""

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ElevationArea, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        obj = self.get_object()
        return obj.get_elevation_area()


class PathLayer(MapEntityLayer):
    model = Path
    properties = ['name']


class PathList(MapEntityList):
    queryset = Path.objects.prefetch_related('networks').select_related('stake', 'trail')
    filterform = PathFilter
    columns = ['id', 'name', 'networks', 'stake', 'trail']


class PathJsonList(MapEntityJsonList, PathList):
    pass


class PathFormatList(MapEntityFormat, PathList):
    pass


class PathDetail(MapEntityDetail):
    model = Path

    def context_data(self, *args, **kwargs):
        context = super(PathDetail, self).context_data(*args, **kwargs)
        context['can_edit'] = self.get_object().same_structure(self.request.user)
        return context


class PathDocument(MapEntityDocument):
    model = Path

    def get_context_data(self, *args, **kwargs):
        self.get_object().prepare_elevation_chart(self.request)
        return super(PathDocument, self).get_context_data(*args, **kwargs)


class PathCreate(MapEntityCreate):
    model = Path
    form_class = PathForm


class PathUpdate(MapEntityUpdate):
    model = Path
    form_class = PathForm

    @same_structure_required('core:path_detail')
    def dispatch(self, *args, **kwargs):
        return super(PathUpdate, self).dispatch(*args, **kwargs)


class PathDelete(MapEntityDelete):
    model = Path

    @same_structure_required('core:path_detail')
    def dispatch(self, *args, **kwargs):
        return super(PathDelete, self).dispatch(*args, **kwargs)


@login_required
@cache_last_modified(lambda x: Path.latest_updated())
@force_cache_validation
def get_graph_json(request):
    cache = get_cache('fat')
    key = 'path_graph_json'

    result = cache.get(key)
    latest = Path.latest_updated()

    if result and latest:
        cache_latest, json_graph = result
        # Not empty and still valid
        if cache_latest and cache_latest >= latest:
            return HttpJSONResponse(json_graph)

    # cache does not exist or is not up to date
    # rebuild the graph and cache the json
    graph = graph_lib.graph_edges_nodes_of_qs(Path.objects.all())
    json_graph = json.dumps(graph)

    cache.set(key, (latest, json_graph))
    return HttpJSONResponse(json_graph)


class TrailList(MapEntityList):
    model = Trail


class TrailDetail(MapEntityDetail):
    model = Trail


class TrailUpdate(MapEntityUpdate):
    model = Trail


class TrailDocument(MapEntityDocument):
    model = Trail
