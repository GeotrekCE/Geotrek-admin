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


class InterventionUpdate(ModuleUpdate):
    model = Intervention
    form_class = InterventionForm


class InterventionDelete(ModuleDelete):
    model = Intervention
