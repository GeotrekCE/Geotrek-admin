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
    columns = ['name', 'date', 'material_cost']


class InterventionJsonList(MapEntityJsonList, InterventionList):
    pass


class InterventionDetail(MapEntityDetail):
    model = Intervention

    def can_edit(self):
        return self.request.user.profile.is_path_manager and \
               self.get_object().same_structure(self.request.user)


class InterventionCreate(MapEntityCreate):
    model = Intervention
    form_class = InterventionForm


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
