from django.utils.decorators import method_decorator
from django.conf import settings
from django.views.generic.list import ListView

from djgeojson.views import GeoJSONLayerView

from caminae.authent.decorators import path_manager_required
from caminae.common.views import JSONResponseMixin
from caminae.mapentity.views import (MapEntityLayer, MapEntityList, MapEntityJsonList, MapEntityFormat,
                                     MapEntityDetail, MapEntityDocument, MapEntityCreate, MapEntityUpdate, MapEntityDelete)

from .models import (PhysicalEdge, LandEdge, CompetenceEdge, WorkManagementEdge, SignageManagementEdge,
                     City, RestrictedArea, District)
from .filters import PhysicalEdgeFilter, LandEdgeFilter, CompetenceEdgeFilter, WorkManagementEdgeFilter, SignageManagementEdgeFilter
from .forms import PhysicalEdgeForm, LandEdgeForm, CompetenceEdgeForm, WorkManagementEdgeForm, SignageManagementEdgeForm


class CityGeoJSONLayer(GeoJSONLayerView):
    model = City
    srid = settings.API_SRID
    precision = settings.LAYER_PRECISION_LAND
    simplify = settings.LAYER_SIMPLIFY_LAND


class RestrictedAreaGeoJSONLayer(GeoJSONLayerView):
    model = RestrictedArea
    srid = settings.API_SRID
    precision = settings.LAYER_PRECISION_LAND
    simplify = settings.LAYER_SIMPLIFY_LAND


class DistrictGeoJSONLayer(GeoJSONLayerView):
    srid = settings.API_SRID
    model = District
    precision = settings.LAYER_PRECISION_LAND
    simplify = settings.LAYER_SIMPLIFY_LAND


class DistrictJSONList(JSONResponseMixin, ListView):
    model = District

    def get_context_data(self, **kwargs):
        context = []
        for district in self.get_queryset():
            context.append(dict(pk=district.pk, name=district.name))
        return context


class PhysicalEdgeLayer(MapEntityLayer):
    queryset = PhysicalEdge.objects.existing()


class PhysicalEdgeList(MapEntityList):
    queryset = PhysicalEdge.objects.existing()
    filterform = PhysicalEdgeFilter
    columns = ['id', 'physical_type']


class PhysicalEdgeJsonList(MapEntityJsonList, PhysicalEdgeList):
    pass


class PhysicalEdgeFormatList(MapEntityFormat, PhysicalEdgeList):
    pass


class PhysicalEdgeDetail(MapEntityDetail):
    model = PhysicalEdge

    def can_edit(self):
        return hasattr(self.request.user, 'profile') and \
               self.request.user.profile.is_path_manager


class PhysicalEdgeDocument(MapEntityDocument):
    model = PhysicalEdge


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
    queryset = LandEdge.objects.existing()


class LandEdgeList(MapEntityList):
    queryset = LandEdge.objects.existing()
    filterform = LandEdgeFilter
    columns = ['id', 'land_type']


class LandEdgeJsonList(MapEntityJsonList, LandEdgeList):
    pass


class LandEdgeFormatList(MapEntityFormat, LandEdgeList):
    pass


class LandEdgeDetail(MapEntityDetail):
    model = LandEdge

    def can_edit(self):
        return hasattr(self.request.user, 'profile') and \
               self.request.user.profile.is_path_manager


class LandEdgeDocument(MapEntityDocument):
    model = LandEdge


class LandEdgeCreate(MapEntityCreate):
    model = LandEdge
    form_class = LandEdgeForm


class LandEdgeUpdate(MapEntityUpdate):
    model = LandEdge
    form_class = LandEdgeForm

    @method_decorator(path_manager_required('land:landedge_detail'))
    def dispatch(self, *args, **kwargs):
        return super(LandEdgeUpdate, self).dispatch(*args, **kwargs)


class LandEdgeDelete(MapEntityDelete):
    model = LandEdge

    @method_decorator(path_manager_required('land:landedge_detail'))
    def dispatch(self, *args, **kwargs):
        return super(LandEdgeDelete, self).dispatch(*args, **kwargs)


class CompetenceEdgeLayer(MapEntityLayer):
    queryset = CompetenceEdge.objects.existing()


class CompetenceEdgeList(MapEntityList):
    queryset = CompetenceEdge.objects.existing()
    filterform = CompetenceEdgeFilter
    columns = ['id', 'organization']


class CompetenceEdgeJsonList(MapEntityJsonList, CompetenceEdgeList):
    pass


class CompetenceEdgeFormatList(MapEntityFormat, CompetenceEdgeList):
    pass


class CompetenceEdgeDetail(MapEntityDetail):
    model = CompetenceEdge

    def can_edit(self):
        return hasattr(self.request.user, 'profile') and \
               self.request.user.profile.is_path_manager


class CompetenceEdgeDocument(MapEntityDocument):
    model = CompetenceEdge


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
    queryset = WorkManagementEdge.objects.existing()


class WorkManagementEdgeList(MapEntityList):
    queryset = WorkManagementEdge.objects.existing()
    filterform = WorkManagementEdgeFilter
    columns = ['id', 'organization']


class WorkManagementEdgeJsonList(MapEntityJsonList, WorkManagementEdgeList):
    pass


class WorkManagementEdgeFormatList(MapEntityFormat, WorkManagementEdgeList):
    pass


class WorkManagementEdgeDetail(MapEntityDetail):
    model = WorkManagementEdge

    def can_edit(self):
        return hasattr(self.request.user, 'profile') and \
               self.request.user.profile.is_path_manager


class WorkManagementEdgeDocument(MapEntityDocument):
    model = WorkManagementEdge


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
    queryset = SignageManagementEdge.objects.existing()


class SignageManagementEdgeList(MapEntityList):
    queryset = SignageManagementEdge.objects.existing()
    filterform = SignageManagementEdgeFilter
    columns = ['id', 'organization']


class SignageManagementEdgeJsonList(MapEntityJsonList, SignageManagementEdgeList):
    pass


class SignageManagementEdgeFormatList(MapEntityFormat, SignageManagementEdgeList):
    pass


class SignageManagementEdgeDetail(MapEntityDetail):
    model = SignageManagementEdge

    def can_edit(self):
        return hasattr(self.request.user, 'profile') and \
               self.request.user.profile.is_path_manager


class SignageManagementEdgeDocument(MapEntityDocument):
    model = SignageManagementEdge


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
