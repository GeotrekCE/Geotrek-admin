# -*- coding: utf-8 -*-
import json
import logging
from collections import defaultdict

from django.contrib.auth.decorators import permission_required
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import last_modified as cache_last_modified
from django.views.decorators.cache import never_cache as force_cache_validation
from django.views.generic import View
from django.utils.translation import ugettext as _
from django.core.cache import caches
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
from django.db.models import Sum
from django.db.models.functions import Coalesce
from geotrek.api.v2.functions import Length
from django.db.models.fields import FloatField


logger = logging.getLogger(__name__)


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
        return ("core/path_list.html",)

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
        return qs


class PathJsonList(MapEntityJsonList, PathList):
    def get_context_data(self, **kwargs):
        context = super(PathJsonList, self).get_context_data(**kwargs)
        context["sumPath"] = round(self.object_list.aggregate(
            sumPath=Coalesce(Sum(Length('geom'), output_field=FloatField()), 0))['sumPath'] / 1000, 1)
        return context


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

    def get_context_data(self, **kwargs):
        context = super(PathDelete, self).get_context_data(**kwargs)
        topologies_by_model = defaultdict(list)
        if 'geotrek.core' in settings.INSTALLED_APPS:
            for trail in self.object.trails:
                topologies_by_model[_('Trails')].append({'name': trail.name, 'url': trail.get_detail_url()})
        if 'geotrek.trekking' in settings.INSTALLED_APPS:
            for trek in self.object.treks:
                topologies_by_model[_('Treks')].append({'name': trek.name, 'url': trek.get_detail_url()})
            for service in self.object.services:
                topologies_by_model[_('Services')].append({'name': service.type.name, 'url': service.get_detail_url()})
            for poi in self.object.pois:
                topologies_by_model[_('Pois')].append({'name': poi.name, 'url': poi.get_detail_url()})
        if 'geotrek.infrastructure' in settings.INSTALLED_APPS:
            for signage in self.object.signages:
                topologies_by_model[_('Signages')].append({'name': signage.name, 'url': signage.get_detail_url()})
            for infrastructure in self.object.infrastructures:
                topologies_by_model[_('Infrastructures')].append({'name': infrastructure.name, 'url': infrastructure.get_detail_url()})
        if 'geotrek.maintenance' in settings.INSTALLED_APPS:
            for intervention in self.object.interventions:
                topologies_by_model[_('Interventions')].append({'name': intervention.name, 'url': intervention.get_detail_url()})
        context['topologies_by_model'] = dict(topologies_by_model)
        return context


@login_required
@cache_last_modified(lambda x: Path.latest_updated())
@force_cache_validation
def get_graph_json(request):
    cache = caches['fat']
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
        ids_path_merge = request.POST.getlist('path[]')

        assert len(ids_path_merge) == 2

        path_a = Path.objects.get(pk=ids_path_merge[0])
        path_b = Path.objects.get(pk=ids_path_merge[1])

        if not path_a.same_structure(request.user) or not path_b.same_structure(request.user):
            response = {'error': _("You don't have the right to change these paths")}
            return HttpJSONResponse(response)

        try:
            result = path_a.merge_path(path_b)
        except Exception as exc:
            response = {'error': exc, }
            return HttpJSONResponse(response)

        if result == 2:
            response = {'error': _("You can't merge 2 paths with a 3rd path in the intersection")}
        elif result == 0:
            response = {'error': _("No matching points to merge paths found")}
        else:
            response = {'success': _("Paths merged successfully")}
            messages.success(request, _("Paths merged successfully"))

        return HttpJSONResponse(response)


class ParametersView(View):
    def get(request, *args, **kwargs):
        response = {
            'geotrek_admin_version': settings.VERSION,
        }
        return HttpResponse(json.dumps(response), content_type="application/json")
