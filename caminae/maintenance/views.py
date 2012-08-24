import logging

from django.utils.decorators import method_decorator

from caminae.authent.decorators import same_structure_required, path_manager_required
from caminae.core.views import (MapEntityLayer, MapEntityList, MapEntityJsonList, 
                                MapEntityDetail, MapEntityCreate, MapEntityUpdate, MapEntityDelete)
from caminae.infrastructure.models import BaseInfrastructure
from .models import Intervention, Project
from .filters import InterventionFilter, ProjectFilter
from .forms import InterventionForm, InterventionCreateForm, ProjectForm


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
        try:
            pk = self.request.GET.get('infrastructure')
            if pk:
                return BaseInfrastructure.objects.get(pk=pk)
        except BaseInfrastructure.DoesNotExist:
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


class InterventionUpdate(MapEntityUpdate):
    model = Intervention
    form_class = InterventionForm

    @same_structure_required('maintenance:intervention_detail')
    @method_decorator(path_manager_required('maintenance:intervention_detail'))
    def dispatch(self, *args, **kwargs):
        return super(InterventionUpdate, self).dispatch(*args, **kwargs)


class InterventionDelete(MapEntityDelete):
    model = Intervention

    @same_structure_required('maintenance:intervention_detail')
    @method_decorator(path_manager_required('maintenance:intervention_detail'))
    def dispatch(self, *args, **kwargs):
        return super(InterventionDelete, self).dispatch(*args, **kwargs)



class ProjectLayer(MapEntityLayer):
    model = Project


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


class ProjectCreate(MapEntityCreate):
    model = Project
    form_class = ProjectForm


class ProjectUpdate(MapEntityUpdate):
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
