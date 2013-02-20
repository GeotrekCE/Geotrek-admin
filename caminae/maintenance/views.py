# -*- coding: utf-8 -*-

import logging

from django.utils.decorators import method_decorator

from caminae.common.views import FormsetMixin
from caminae.authent.decorators import same_structure_required, path_manager_required
from caminae.core.views import (MapEntityLayer, MapEntityList, MapEntityJsonList, MapEntityFormat,
                                MapEntityDetail, MapEntityDocument, MapEntityCreate, MapEntityUpdate, MapEntityDelete)
from caminae.infrastructure.models import Infrastructure, Signage
from .models import Intervention, Project
from .filters import InterventionFilter, ProjectFilter
from .forms import (InterventionForm, InterventionCreateForm, ProjectForm,
                    FundingFormSet, ManDayFormSet)


logger = logging.getLogger(__name__)


class InterventionLayer(MapEntityLayer):
    queryset = Intervention.objects.existing()


class InterventionList(MapEntityList):
    queryset = Intervention.objects.existing()
    filterform = InterventionFilter
    columns = ['id', 'name', 'date', 'type', 'infrastructure', 'status', 'stake']


class InterventionJsonList(MapEntityJsonList, InterventionList):
    pass


class InterventionFormatList(MapEntityFormat, InterventionList):
    pass


class InterventionDetail(MapEntityDetail):
    queryset = Intervention.objects.existing()

    def can_edit(self):
        return self.request.user.is_staff or \
               (hasattr(self.request.user, 'profile') and \
                self.request.user.profile.is_path_manager and \
                self.get_object().same_structure(self.request.user))


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
    queryset = Intervention.objects.existing()
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
    columns = ['id', 'name', 'period', 'type', 'domain']


class ProjectJsonList(MapEntityJsonList, ProjectList):
    pass


class ProjectFormatList(MapEntityFormat, ProjectList):
    pass


class ProjectDetail(MapEntityDetail):
    queryset = Project.objects.existing()

    def can_edit(self):
        return self.request.user.is_staff or \
               (hasattr(self.request.user, 'profile') and \
                self.request.user.profile.is_path_manager and \
            self.get_object().same_structure(self.request.user))


class ProjectDocument(MapEntityDocument):
    model = Project


class FundingFormsetMixin(FormsetMixin):
    context_name = 'funding_formset'
    formset_class = FundingFormSet


class ProjectCreate(FundingFormsetMixin, MapEntityCreate):
    model = Project
    form_class = ProjectForm


class ProjectUpdate(FundingFormsetMixin, MapEntityUpdate):
    queryset = Project.objects.existing()
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
