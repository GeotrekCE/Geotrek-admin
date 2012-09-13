# -*- coding: utf-8 -*-

import logging

from django.utils.decorators import method_decorator
from django.contrib.gis.geos import LineString, Point

from caminae.common.views import FormsetMixin
from caminae.authent.decorators import same_structure_required, path_manager_required
from caminae.core.models import TopologyMixin
from caminae.core.views import (MapEntityLayer, MapEntityList, MapEntityJsonList, MapEntityFormat,
                                MapEntityDetail, MapEntityDocument, MapEntityCreate, MapEntityUpdate, MapEntityDelete)
from caminae.infrastructure.models import Infrastructure, Signage
from .models import Intervention, Project
from .filters import InterventionFilter, ProjectFilter
from .forms import (InterventionForm, InterventionCreateForm, ProjectForm,
                    FundingFormSet, ManDayFormSet)

from caminae.mapentity import shape_exporter

logger = logging.getLogger(__name__)


class InterventionLayer(MapEntityLayer):
    queryset = Intervention.objects.existing()


class InterventionList(MapEntityList):
    queryset = Intervention.objects.existing()
    filterform = InterventionFilter
    columns = ['id', 'name', 'date', 'material_cost']


class InterventionJsonList(MapEntityJsonList, InterventionList):
    pass


class InterventionFormatList(MapEntityFormat, InterventionList):

    def get_geom_info(self, model):
        get_geom, geom_type, srid = super(InterventionFormatList, self).get_geom_info(TopologyMixin)
        # get_geom returns how to get a geom from a topology, so we give him if we got one
        new_get_geom = lambda obj: get_geom(obj.topology) if obj.topology else None

        return new_get_geom, geom_type, srid

class InterventionDetail(MapEntityDetail):
    model = Intervention

    def can_edit(self):
        return self.request.user.profile.is_path_manager and \
               self.get_object().same_structure(self.request.user)


class InterventionDocument(MapEntityDocument):
    model = Intervention


class ManDayFormsetMixin(FormsetMixin):
    context_name = 'manday_formset'
    formset_class = ManDayFormSet


class InterventionCreate(ManDayFormsetMixin, MapEntityCreate):
    model = Intervention
    form_class = InterventionCreateForm

    def on_infrastucture(self):
        pk = self.request.GET.get('infrastructure')
        if pk:
            try:
                return Infrastructure.objects.existing().get(pk=pk)
            except Infrastructure.DoesNotExist:
                try:
                    return Signage.objects.existing().get(pk=pk)
                except Signage.DoesNotExist:
                    logger.warning("Intervention on unknown infrastructure %s" % pk)
        return None

    def get_initial(self):
        """
        Returns the initial data to use for forms on this view.
        """
        initial = self.initial.copy()
        infrastructure = self.on_infrastucture()
        if infrastructure:
            initial['infrastructure'] = infrastructure
        return initial

    def get_context_data(self, **kwargs):
        context = super(InterventionCreate, self).get_context_data(**kwargs)
        context['infrastructure'] = self.on_infrastucture()
        return context


class InterventionUpdate(ManDayFormsetMixin, MapEntityUpdate):
    model = Intervention
    form_class = InterventionForm

    @same_structure_required('maintenance:intervention_detail')
    @method_decorator(path_manager_required('maintenance:intervention_detail'))
    def dispatch(self, *args, **kwargs):
        return super(InterventionUpdate, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(InterventionUpdate, self).get_context_data(**kwargs)
        context['infrastructure'] = self.object.infrastructure
        return context


class InterventionDelete(MapEntityDelete):
    model = Intervention

    @same_structure_required('maintenance:intervention_detail')
    @method_decorator(path_manager_required('maintenance:intervention_detail'))
    def dispatch(self, *args, **kwargs):
        return super(InterventionDelete, self).dispatch(*args, **kwargs)



class ProjectLayer(MapEntityLayer):
    queryset = Project.objects.existing()

    def get_queryset(self):
        nonemptyqs = Intervention.objects.existing().filter(project__isnull=False).values('project')
        return super(ProjectLayer, self).get_queryset().filter(pk__in=nonemptyqs)


class ProjectList(MapEntityList):
    queryset = Project.objects.existing()
    filterform = ProjectFilter
    columns = ['id', 'name', 'begin_year', 'end_year', 'cost']


class ProjectJsonList(MapEntityJsonList, ProjectList):
    pass


class ProjectFormatList(MapEntityFormat, ProjectList):
    """
    For exporting shapes, our iterables will return ** tuples (project, intervention) **.
    """

    def split_points_linestrings(self, queryset, get_geom):
        """Yield tuple (project, intervention) - not project /!\ """
        def gen_from_geom(geom_class):
            for project in queryset:
                for it in project.interventions.all():
                    if it.geom and isinstance(it.geom, geom_class):
                        yield (project, it)

        return gen_from_geom(Point), gen_from_geom(LineString)

    def get_geom_info(self, model):
        get_geom, geom_type, srid = super(ProjectFormatList, self).get_geom_info(TopologyMixin)

        # project_it being: (project, it)
        new_get_geom = lambda project_it: get_geom(project_it[1].topology) if project_it[1].topology else None

        return new_get_geom, geom_type, srid

    def get_fieldmap(self, qs):
        fieldmap = shape_exporter.fieldmap_from_fields(qs.model, self.columns)

        # project_it being: (project, it)

        # As we will get interventions from iterable convert to project
        fieldmap_from_project_it = dict(
                (k, lambda project_it, getter=project_getter: getter(project_it[0]))
                for k, project_getter in fieldmap.iteritems())

        # project_it[1] => use current intervention
        fieldmap_from_project_it['it_pk'] = lambda project_it: str(project_it[1].pk)
        fieldmap_from_project_it['it_name'] = lambda project_it: str(project_it[1].name)

        return fieldmap_from_project_it


class ProjectDetail(MapEntityDetail):
    model = Project

    def can_edit(self):
        return self.request.user.profile.is_path_manager and \
               self.get_object().same_structure(self.request.user)


class ProjectDocument(MapEntityDocument):
    model = Project


class FundingFormsetMixin(FormsetMixin):
    context_name = 'funding_formset'
    formset_class = FundingFormSet


class ProjectCreate(FundingFormsetMixin, MapEntityCreate):
    model = Project
    form_class = ProjectForm


class ProjectUpdate(FundingFormsetMixin, MapEntityUpdate):
    model = Project
    form_class = ProjectForm

    @same_structure_required('maintenance:project_detail')
    @method_decorator(path_manager_required('maintenance:project_detail'))
    def dispatch(self, *args, **kwargs):
        return super(ProjectUpdate, self).dispatch(*args, **kwargs)


class ProjectDelete(MapEntityDelete):
    model = Project

    @same_structure_required('maintenance:project_detail')
    @method_decorator(path_manager_required('maintenance:project_detail'))
    def dispatch(self, *args, **kwargs):
        return super(ProjectDelete, self).dispatch(*args, **kwargs)
