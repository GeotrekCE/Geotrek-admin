import logging

from django.utils.decorators import method_decorator
from django.http import HttpResponseRedirect

from caminae.authent.decorators import same_structure_required, path_manager_required
from caminae.core.views import (MapEntityLayer, MapEntityList, MapEntityJsonList, 
                                MapEntityDetail, MapEntityCreate, MapEntityUpdate, MapEntityDelete)
from caminae.infrastructure.models import Infrastructure, Signage
from .models import Intervention, Project
from .filters import InterventionFilter, ProjectFilter
from .forms import (InterventionForm, InterventionCreateForm, ProjectForm,
                    FundingFormSet)


logger = logging.getLogger(__name__)


class InterventionLayer(MapEntityLayer):
    model = Intervention


class InterventionList(MapEntityList):
    model = Intervention
    filterform = InterventionFilter
    columns = ['id', 'name', 'date', 'material_cost']


class InterventionJsonList(MapEntityJsonList, InterventionList):
    pass


class InterventionDetail(MapEntityDetail):
    model = Intervention

    def can_edit(self):
        return self.request.user.profile.is_path_manager and \
               self.get_object().same_structure(self.request.user)


class InterventionCreate(MapEntityCreate):
    model = Intervention
    form_class = InterventionCreateForm

    def on_infrastucture(self):
        pk = self.request.GET.get('infrastructure')
        if pk:
            try:
                return Infrastructure.objects.get(pk=pk)
            except Infrastructure.DoesNotExist:
                try:
                    return Signage.objects.get(pk=pk)
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


class InterventionUpdate(MapEntityUpdate):
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
    model = Project

    def get_queryset(self):
        nonemptyqs = Intervention.objects.filter(project__isnull=False).values('project')
        return super(ProjectLayer, self).get_queryset().filter(pk__in=nonemptyqs)


class ProjectList(MapEntityList):
    model = Project
    filterform = ProjectFilter
    columns = ['id', 'name', 'begin_year', 'end_year', 'cost']


class ProjectJsonList(MapEntityJsonList, ProjectList):
    pass


class ProjectDetail(MapEntityDetail):
    model = Project

    def can_edit(self):
        return self.request.user.profile.is_path_manager and \
               self.get_object().same_structure(self.request.user)


class FundingFormsetMixin(object):
    def form_valid(self, form):
        context = self.get_context_data()
        funding_form = context['funding_formset']
        
        if funding_form.is_valid():
            self.object = form.save()
            funding_form.instance = self.object
            funding_form.save()
            return HttpResponseRedirect(self.get_success_url())
        else:
            return self.render_to_response(self.get_context_data(form=form))

    def get_context_data(self, **kwargs):
        context = super(FundingFormsetMixin, self).get_context_data(**kwargs)
        if self.request.POST:
            context['funding_formset'] = FundingFormSet(self.request.POST, instance=self.object)
        else:
            context['funding_formset'] = FundingFormSet(instance=self.object)
        return context


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
