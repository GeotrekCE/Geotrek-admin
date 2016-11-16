# -*- coding: utf-8 -*-

import json
import logging

from django.contrib.auth.decorators import permission_required
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import last_modified as cache_last_modified
from django.views.decorators.cache import never_cache as force_cache_validation
from django.views.generic import View
from django.utils.translation import ugettext as _
from django.core.cache import get_cache
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from mapentity import registry
from mapentity.views import (MapEntityLayer, MapEntityList, MapEntityJsonList,
                             MapEntityDetail, MapEntityDocument, MapEntityCreate, MapEntityUpdate,
                             MapEntityDelete, MapEntityFormat,
                             HttpJSONResponse)

from geotrek.authent.decorators import same_structure_required
from geotrek.common.utils import classproperty
from geotrek.core.models import AltimetryMixin

from .models import Path, Trail, Topology
from .forms import PathForm, TrailForm
from .filters import PathFilterSet, TrailFilterSet
from . import graph as graph_lib
from django.http.response import HttpResponse
from django.contrib import messages


logger = logging.getLogger(__name__)


@login_required
def last_list(request):
    last = request.session.get('last_list')  # set in MapEntityList
    for entity in registry.entities:
        if reverse(entity.url_list) == last and request.user.has_perm(entity.model.get_permission_codename('list')):
            return redirect(entity.url_list)
    for entity in registry.entities:
        if request.user.has_perm(entity.model.get_permission_codename('list')):
            return redirect(entity.url_list)
    return redirect('trekking:trek_list')


home = last_list


class CreateFromTopologyMixin(object):
    def on_topology(self):
        pk = self.request.GET.get('topology')
        if pk:
            try:
                return Topology.objects.existing().get(pk=pk)
            except Topology.DoesNotExist:
                logger.warning("Intervention on unknown topology %s" % pk)
        return None

    def get_initial(self):
        initial = super(CreateFromTopologyMixin, self).get_initial()
        # Create intervention with an existing topology as initial data
        topology = self.on_topology()
        if topology:
            initial['topology'] = topology.serialize(with_pk=False)
        return initial


class PathLayer(MapEntityLayer):
    model = Path
    properties = ['name']


class PathList(MapEntityList):
    queryset = Path.objects.prefetch_related('networks').select_related('stake')
    filterform = PathFilterSet

    @classproperty
    def columns(cls):
        columns = ['id', 'checkbox', 'name', 'networks', 'length', 'length_2d']
        if settings.TRAIL_MODEL_ENABLED:
            columns.append('trails')
        return columns

    def get_template_names(self):
        return (u"core/path_list.html",)

    def get_queryset(self):
        """
        denormalize ``trail`` column from list.
        """
        qs = super(PathList, self).get_queryset()

        denormalized = {}
        if settings.TRAIL_MODEL_ENABLED:
            paths_id = qs.values_list('id', flat=True)
            paths_trails = Trail.objects.filter(aggregations__path__id__in=paths_id)
            by_id = dict([(trail.id, trail) for trail in paths_trails])
            trails_paths_ids = paths_trails.values_list('id', 'aggregations__path__id')
            for trail_id, path_id in trails_paths_ids:
                denormalized.setdefault(path_id, []).append(by_id[trail_id])

        for path in qs:
            path_trails = denormalized.get(path.id, [])
            setattr(path, '_trails', path_trails)
            yield path


class PathJsonList(MapEntityJsonList, PathList):
    pass


class PathFormatList(MapEntityFormat, PathList):
    columns = [
        'id', 'valid', 'visible', 'name', 'comments', 'departure', 'arrival',
        'comfort', 'source', 'stake', 'usages', 'networks',
        'structure', 'date_insert', 'date_update',
        'cities', 'districts', 'areas', 'length_2d'
    ] + AltimetryMixin.COLUMNS


class PathDetail(MapEntityDetail):
    model = Path

    def get_context_data(self, *args, **kwargs):
        context = super(PathDetail, self).get_context_data(*args, **kwargs)
        context['can_edit'] = self.get_object().same_structure(self.request.user)
        return context


class PathDocument(MapEntityDocument):
    model = Path

    def get_context_data(self, *args, **kwargs):
        language = self.request.LANGUAGE_CODE
        self.get_object().prepare_elevation_chart(language, self.request.build_absolute_uri('/'))
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


class TrailLayer(MapEntityLayer):
    queryset = Trail.objects.existing()
    properties = ['name']


class TrailList(MapEntityList):
    queryset = Trail.objects.existing()
    filterform = TrailFilterSet
    columns = ['id', 'name', 'departure', 'arrival', 'length']


class TrailJsonList(MapEntityJsonList, TrailList):
    pass


class TrailFormatList(MapEntityFormat, TrailList):
    columns = [
        'id', 'name', 'comments', 'departure', 'arrival',
        'structure', 'date_insert', 'date_update',
        'cities', 'districts', 'areas',
    ] + AltimetryMixin.COLUMNS


class TrailDetail(MapEntityDetail):
    queryset = Trail.objects.existing()

    def get_context_data(self, *args, **kwargs):
        context = super(TrailDetail, self).get_context_data(*args, **kwargs)
        context['can_edit'] = self.get_object().same_structure(self.request.user)
        return context


class TrailDocument(MapEntityDocument):
    queryset = Trail.objects.existing()


class TrailCreate(CreateFromTopologyMixin, MapEntityCreate):
    model = Trail
    form_class = TrailForm


class TrailUpdate(MapEntityUpdate):
    queryset = Trail.objects.existing()
    form_class = TrailForm

    @same_structure_required('core:trail_detail')
    def dispatch(self, *args, **kwargs):
        return super(TrailUpdate, self).dispatch(*args, **kwargs)


class TrailDelete(MapEntityDelete):
    queryset = Trail.objects.existing()

    @same_structure_required('core:trail_detail')
    def dispatch(self, *args, **kwargs):
        return super(TrailDelete, self).dispatch(*args, **kwargs)


@permission_required('core.change_path')
def merge_path(request):
    """
    Path merging view
    """
    response = {}

    if request.method == 'POST':
        try:
            ids_path_merge = request.POST.getlist('path[]')

            if len(ids_path_merge) == 2:
                path_a = Path.objects.get(pk=ids_path_merge[0])
                path_b = Path.objects.get(pk=ids_path_merge[1])
                if not path_a.same_structure(request.user) or not path_b.same_structure(request.user):
                    response = {'error': _(u"You don't have the right to change these paths")}

                elif path_a.merge_path(path_b):
                    response = {'success': _(u"Paths merged successfully")}
                    messages.success(request, _(u"Paths merged successfully"))

                else:
                    response = {'error': _(u"No matching points to merge paths found")}

            else:
                raise

        except Exception as exc:
            response = {'error': exc, }

    return HttpResponse(json.dumps(response), mimetype="application/json")


class ParametersView(View):
    def get(request, *args, **kwargs):
        response = {
            'geotrek_admin_version': settings.VERSION,
        }
        return HttpResponse(json.dumps(response), mimetype="application/json")
