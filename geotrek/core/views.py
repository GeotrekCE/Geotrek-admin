# -*- coding: utf-8 -*-
import json
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import last_modified as cache_last_modified
from django.views.decorators.cache import never_cache as force_cache_validation
from django.core.cache import get_cache
from django.shortcuts import redirect

from mapentity.views import (MapEntityLayer, MapEntityList, MapEntityJsonList,
                             MapEntityDetail, MapEntityDocument, MapEntityCreate, MapEntityUpdate,
                             MapEntityDelete, MapEntityFormat,
                             HttpJSONResponse)

from geotrek.authent.decorators import same_structure_required

from .models import Path, Trail
from .forms import PathForm
from .filters import PathFilterSet
from . import graph as graph_lib


@login_required
def last_list(request):
    last = request.session.get('last_list')  # set in MapEntityList
    if not last:
        return redirect('core:path_list')
    return redirect(last)

home = last_list


class PathLayer(MapEntityLayer):
    model = Path
    properties = ['name']


class PathList(MapEntityList):
    queryset = Path.objects.prefetch_related('networks').select_related('stake', 'trail')
    filterform = PathFilterSet
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
