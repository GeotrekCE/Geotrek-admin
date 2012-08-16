from django.utils.decorators import method_decorator

from caminae.authent.decorators import same_structure_required, path_manager_required
from caminae.core.views import (MapEntityLayer, MapEntityList, MapEntityJsonList, 
                                MapEntityDetail, MapEntityCreate, MapEntityUpdate, MapEntityDelete)

from .models import PhysicalEdge, LandEdge, CompetenceEdge, WorkManagementEdge, SignageManagementEdge
from .filters import PhysicalEdgeFilter, LandEdgeFilter, CompetenceEdgeFilter, WorkManagementEdgeFilter, SignageManagementEdgeFilter
from .forms import PhysicalEdgeForm, LandEdgeForm, CompetenceEdgeForm, WorkManagementEdgeForm, SignageManagementEdgeForm


class PhysicalEdgeLayer(MapEntityLayer):
    model = PhysicalEdge


class PhysicalEdgeList(MapEntityList):
    model = PhysicalEdge
    filterform = PhysicalEdgeFilter
    columns = ['physical_type']


class PhysicalEdgeJsonList(MapEntityJsonList, PhysicalEdgeList):
    pass


class PhysicalEdgeDetail(MapEntityDetail):
    model = PhysicalEdge

    def can_edit(self):
        return self.request.user.profile.is_path_manager


class PhysicalEdgeCreate(MapEntityCreate):
    model = PhysicalEdge
    form_class = PhysicalEdgeForm


class PhysicalEdgeUpdate(MapEntityUpdate):
    model = PhysicalEdge
    form_class = PhysicalEdgeForm

    @method_decorator(path_manager_required('land:physicaledge_detail'))
    def dispatch(self, *args, **kwargs):
        return super(PhysicalEdgeUpdate, self).dispatch(*args, **kwargs)


class PhysicalEdgeDelete(MapEntityDelete):
    model = PhysicalEdge

    @method_decorator(path_manager_required('land:physicaledge_detail'))
    def dispatch(self, *args, **kwargs):
        return super(PhysicalEdgeDelete, self).dispatch(*args, **kwargs)


class LandEdgeLayer(MapEntityLayer):
    model = LandEdge


class LandEdgeList(MapEntityList):
    model = LandEdge
    filterform = LandEdgeFilter
    columns = ['land_type']


class LandEdgeJsonList(MapEntityJsonList, LandEdgeList):
    pass


class LandEdgeDetail(MapEntityDetail):
    model = LandEdge

    def can_edit(self):
        return self.request.user.profile.is_path_manager  and \
               self.get_object().same_structure(self.request.user)


class LandEdgeCreate(MapEntityCreate):
    model = LandEdge
    form_class = LandEdgeForm


class LandEdgeUpdate(MapEntityUpdate):
    model = LandEdge
    form_class = LandEdgeForm

    @same_structure_required('land:landedge_detail')
    @method_decorator(path_manager_required('land:landedge_detail'))
    def dispatch(self, *args, **kwargs):
        return super(LandEdgeUpdate, self).dispatch(*args, **kwargs)


class LandEdgeDelete(MapEntityDelete):
    model = LandEdge

    @same_structure_required('land:landedge_detail')
    @method_decorator(path_manager_required('land:landedge_detail'))
    def dispatch(self, *args, **kwargs):
        return super(LandEdgeDelete, self).dispatch(*args, **kwargs)


class CompetenceEdgeLayer(MapEntityLayer):
    model = CompetenceEdge


class CompetenceEdgeList(MapEntityList):
    model = CompetenceEdge
    filterform = CompetenceEdgeFilter
    columns = ['organization']


class CompetenceEdgeJsonList(MapEntityJsonList, CompetenceEdgeList):
    pass


class CompetenceEdgeDetail(MapEntityDetail):
    model = CompetenceEdge

    def can_edit(self):
        return self.request.user.profile.is_path_manager


class CompetenceEdgeCreate(MapEntityCreate):
    model = CompetenceEdge
    form_class = CompetenceEdgeForm


class CompetenceEdgeUpdate(MapEntityUpdate):
    model = CompetenceEdge
    form_class = CompetenceEdgeForm

    @method_decorator(path_manager_required('land:competenceedge_detail'))
    def dispatch(self, *args, **kwargs):
        return super(CompetenceEdgeUpdate, self).dispatch(*args, **kwargs)


class CompetenceEdgeDelete(MapEntityDelete):
    model = CompetenceEdge

    @method_decorator(path_manager_required('land:competenceedge_detail'))
    def dispatch(self, *args, **kwargs):
        return super(CompetenceEdgeDelete, self).dispatch(*args, **kwargs)


class WorkManagementEdgeLayer(MapEntityLayer):
    model = WorkManagementEdge


class WorkManagementEdgeList(MapEntityList):
    model = WorkManagementEdge
    filterform = WorkManagementEdgeFilter
    columns = ['organization']


class WorkManagementEdgeJsonList(MapEntityJsonList, WorkManagementEdgeList):
    pass


class WorkManagementEdgeDetail(MapEntityDetail):
    model = WorkManagementEdge

    def can_edit(self):
        return self.request.user.profile.is_path_manager


class WorkManagementEdgeCreate(MapEntityCreate):
    model = WorkManagementEdge
    form_class = WorkManagementEdgeForm


class WorkManagementEdgeUpdate(MapEntityUpdate):
    model = WorkManagementEdge
    form_class = WorkManagementEdgeForm

    @method_decorator(path_manager_required('land:workmanagementedge_detail'))
    def dispatch(self, *args, **kwargs):
        return super(WorkManagementEdgeUpdate, self).dispatch(*args, **kwargs)


class WorkManagementEdgeDelete(MapEntityDelete):
    model = WorkManagementEdge

    @method_decorator(path_manager_required('land:workmanagementedge_detail'))
    def dispatch(self, *args, **kwargs):
        return super(WorkManagementEdgeDelete, self).dispatch(*args, **kwargs)


class SignageManagementEdgeLayer(MapEntityLayer):
    model = SignageManagementEdge


class SignageManagementEdgeList(MapEntityList):
    model = SignageManagementEdge
    filterform = SignageManagementEdgeFilter
    columns = ['organization']


class SignageManagementEdgeJsonList(MapEntityJsonList, SignageManagementEdgeList):
    pass


class SignageManagementEdgeDetail(MapEntityDetail):
    model = SignageManagementEdge

    def can_edit(self):
        return self.request.user.profile.is_path_manager


class SignageManagementEdgeCreate(MapEntityCreate):
    model = SignageManagementEdge
    form_class = SignageManagementEdgeForm


class SignageManagementEdgeUpdate(MapEntityUpdate):
    model = SignageManagementEdge
    form_class = SignageManagementEdgeForm

    @method_decorator(path_manager_required('land:signagemanagementedge_detail'))
    def dispatch(self, *args, **kwargs):
        return super(SignageManagementEdgeUpdate, self).dispatch(*args, **kwargs)


class SignageManagementEdgeDelete(MapEntityDelete):
    model = SignageManagementEdge

    @method_decorator(path_manager_required('land:signagemanagementedge_detail'))
    def dispatch(self, *args, **kwargs):
        return super(SignageManagementEdgeDelete, self).dispatch(*args, **kwargs)
