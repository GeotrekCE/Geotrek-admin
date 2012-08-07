from caminae.authent.decorators import same_structure_required
from caminae.core.views import (ModuleLayer, ModuleList, ModuleJsonList, 
                                ModuleDetail, ModuleCreate, ModuleUpdate, ModuleDelete)
from .models import Intervention
from .filters import InterventionFilter
from .forms import InterventionForm


class InterventionLayer(ModuleLayer):
    model = Intervention


class InterventionList(ModuleList):
    model = Intervention
    filterform = InterventionFilter
    columns = ['name', 'stake', 'typology', 'material_cost']


class InterventionJsonList(ModuleJsonList, InterventionList):
    pass


class InterventionDetail(ModuleDetail):
    model = Intervention


class InterventionCreate(ModuleCreate):
    model = Intervention
    form_class = InterventionForm

    @same_structure_required('maintenance:intervention_list')
    def dispatch(self, *args, **kwargs):
        return super(InterventionCreate, self).dispatch(*args, **kwargs)


class InterventionUpdate(ModuleUpdate):
    model = Intervention
    form_class = InterventionForm

    @same_structure_required('maintenance:intervention_detail')
    def dispatch(self, *args, **kwargs):
        return super(InterventionUpdate, self).dispatch(*args, **kwargs)


class InterventionDelete(ModuleDelete):
    model = Intervention

    @same_structure_required('maintenance:intervention_detail')
    def dispatch(self, *args, **kwargs):
        return super(InterventionDelete, self).dispatch(*args, **kwargs)
