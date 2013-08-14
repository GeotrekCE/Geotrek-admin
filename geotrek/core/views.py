# -*- coding: utf-8 -*-
import math

import json
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import last_modified as cache_last_modified
from django.views.generic.edit import BaseDetailView
from django.core.cache import get_cache
from django.shortcuts import redirect

from mapentity.views import (MapEntityLayer, MapEntityList, MapEntityJsonList,
                             MapEntityDetail, MapEntityDocument, MapEntityCreate, MapEntityUpdate,
                             MapEntityDelete, MapEntityFormat,
                             JSONResponseMixin, HttpJSONResponse, LastModifiedMixin)

from geotrek.authent.decorators import path_manager_required, same_structure_required

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
    def __init__(self, content='', **kwargs):
        kwargs['content_type'] = 'image/svg+xml'
        super(HttpSVGResponse, self).__init__(content, **kwargs)


class ElevationChart(LastModifiedMixin, BaseDetailView):
    def render_to_response(self, context, **response_kwargs):
        return HttpSVGResponse(self.get_object().get_elevation_profile_svg(),
                               **response_kwargs)


class ElevationProfile(LastModifiedMixin, JSONResponseMixin, BaseDetailView):
    """Extract elevation profile from a path and return it as JSON"""

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

    def can_edit(self):
        return self.request.user.is_superuser or \
               (hasattr(self.request.user, 'profile') and \
                self.request.user.profile.is_path_manager and \
                self.get_object().same_structure(self.request.user))


class PathDocument(MapEntityDocument):
    model = Path


class PathCreate(MapEntityCreate):
    model = Path
    form_class = PathForm

    @method_decorator(path_manager_required('core:path_list'))
    def dispatch(self, *args, **kwargs):
        return super(PathCreate, self).dispatch(*args, **kwargs)


class PathUpdate(MapEntityUpdate):
    model = Path
    form_class = PathForm

    @method_decorator(path_manager_required('core:path_detail'))
    @same_structure_required('core:path_detail')
    def dispatch(self, *args, **kwargs):
        return super(PathUpdate, self).dispatch(*args, **kwargs)


class PathDelete(MapEntityDelete):
    model = Path

    @method_decorator(path_manager_required('core:path_detail'))
    @same_structure_required('core:path_detail')
    def dispatch(self, *args, **kwargs):
        return super(PathDelete, self).dispatch(*args, **kwargs)


@cache_last_modified(lambda x: Path.latest_updated())
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
    def path_modifier(path):
        l = 0.0 if math.isnan(path.length) else path.length
        return { "id": path.pk, "length": l}

    graph = graph_lib.graph_edges_nodes_of_qs(
                Path.objects.all(),
                value_modifier=path_modifier,
                key_modifier=graph_lib.get_key_optimizer())
    json_graph = json.dumps(graph)

    cache.set(key, (latest, json_graph))
    return HttpJSONResponse(json_graph)


class TrailDetail(MapEntityDetail):
    model = Trail

    def can_edit(self):
        return False


class TrailDocument(MapEntityDocument):
    model = Trail
