from caminae.authent.decorators import same_structure_required
from caminae.core.views import (MapEntityLayer, MapEntityList, MapEntityJsonList, 
                                MapEntityDetail, MapEntityCreate, MapEntityUpdate, MapEntityDelete)
from .models import Intervention
from .filters import InterventionFilter
from .forms import InterventionForm


class InterventionLayer(MapEntityLayer):
    model = Intervention


class InterventionList(MapEntityList):
    model = Intervention
    filterform = InterventionFilter
    columns = ['name', 'stake', 'typology', 'material_cost']


class InterventionJsonList(MapEntityJsonList, InterventionList):
    pass


class InterventionDetail(MapEntityDetail):
    model = Intervention


class InterventionCreate(MapEntityCreate):
    model = Intervention
    form_class = InterventionForm

    @same_structure_required('maintenance:intervention_list')
    def dispatch(self, *args, **kwargs):
        return super(InterventionCreate, self).dispatch(*args, **kwargs)


class InterventionUpdate(MapEntityUpdate):
    model = Intervention
    form_class = InterventionForm

    @same_structure_required('maintenance:intervention_detail')
    def dispatch(self, *args, **kwargs):
        return super(InterventionUpdate, self).dispatch(*args, **kwargs)


class InterventionDelete(MapEntityDelete):
    model = Intervention

    @same_structure_required('maintenance:intervention_detail')
    def dispatch(self, *args, **kwargs):
        return super(InterventionDelete, self).dispatch(*args, **kwargs)
