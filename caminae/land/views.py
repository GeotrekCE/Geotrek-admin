from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.conf import settings

from djgeojson.views import GeoJSONLayerView

from caminae.authent.decorators import path_manager_required
from caminae.mapentity.views import (MapEntityLayer, MapEntityList, MapEntityJsonList, MapEntityFormat,
                                     MapEntityDetail, MapEntityDocument, MapEntityCreate, MapEntityUpdate, MapEntityDelete)

from .models import (PhysicalEdge, LandEdge, CompetenceEdge, WorkManagementEdge, SignageManagementEdge,
                     City, RestrictedArea, District)
from .filters import PhysicalEdgeFilter, LandEdgeFilter, CompetenceEdgeFilter, WorkManagementEdgeFilter, SignageManagementEdgeFilter
from .forms import PhysicalEdgeForm, LandEdgeForm, CompetenceEdgeForm, WorkManagementEdgeForm, SignageManagementEdgeForm


class LandLayerMixin(object):
    srid = settings.API_SRID
    precision = settings.LAYER_PRECISION_LAND
    simplify = settings.LAYER_SIMPLIFY_LAND

    @method_decorator(cache_page(60 * 60 * 24, cache="fat"))
    def dispatch(self, request, *args, **kwargs):
        return super(LandLayerMixin, self).dispatch(request, *args, **kwargs)


class CityGeoJSONLayer(LandLayerMixin, GeoJSONLayerView):
    model = City


class RestrictedAreaGeoJSONLayer(LandLayerMixin, GeoJSONLayerView):
    model = RestrictedArea


class DistrictGeoJSONLayer(LandLayerMixin, GeoJSONLayerView):
    model = District
    fields = ['name']


class PhysicalEdgeLayer(MapEntityLayer):
    queryset = PhysicalEdge.objects.existing()
    fields = ['color_index', 'name']


class PhysicalEdgeList(MapEntityList):
    queryset = PhysicalEdge.objects.existing()
    filterform = PhysicalEdgeFilter
    columns = ['id', 'physical_type']


class PhysicalEdgeJsonList(MapEntityJsonList, PhysicalEdgeList):
    pass


class PhysicalEdgeFormatList(MapEntityFormat, PhysicalEdgeList):
    pass


class PhysicalEdgeDetail(MapEntityDetail):
    queryset = PhysicalEdge.objects.existing()

    def can_edit(self):
        return self.request.user.is_superuser or \
            (hasattr(self.request.user, 'profile') and
             self.request.user.profile.is_path_manager)


class PhysicalEdgeDocument(MapEntityDocument):
    model = PhysicalEdge


class PhysicalEdgeCreate(MapEntityCreate):
    model = PhysicalEdge
    form_class = PhysicalEdgeForm


class PhysicalEdgeUpdate(MapEntityUpdate):
    queryset = PhysicalEdge.objects.existing()
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
    fields = ['color_index', 'name']


class LandEdgeList(MapEntityList):
    queryset = LandEdge.objects.existing()
    filterform = LandEdgeFilter
    columns = ['id', 'land_type']


class LandEdgeJsonList(MapEntityJsonList, LandEdgeList):
    pass


class LandEdgeFormatList(MapEntityFormat, LandEdgeList):
    pass


class LandEdgeDetail(MapEntityDetail):
    queryset = LandEdge.objects.existing()

    def can_edit(self):
        return self.request.user.is_superuser or \
           (hasattr(self.request.user, 'profile') and
            self.request.user.profile.is_path_manager)


class LandEdgeDocument(MapEntityDocument):
    model = LandEdge


class LandEdgeCreate(MapEntityCreate):
    model = LandEdge
    form_class = LandEdgeForm


class LandEdgeUpdate(MapEntityUpdate):
    queryset = LandEdge.objects.existing()
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
    fields = ['color_index', 'name']


class CompetenceEdgeList(MapEntityList):
    queryset = CompetenceEdge.objects.existing()
    filterform = CompetenceEdgeFilter
    columns = ['id', 'organization']


class CompetenceEdgeJsonList(MapEntityJsonList, CompetenceEdgeList):
    pass


class CompetenceEdgeFormatList(MapEntityFormat, CompetenceEdgeList):
    pass


class CompetenceEdgeDetail(MapEntityDetail):
    queryset = CompetenceEdge.objects.existing()

    def can_edit(self):
        return self.request.user.is_superuser or \
               (hasattr(self.request.user, 'profile') and \
                self.request.user.profile.is_path_manager)


class CompetenceEdgeDocument(MapEntityDocument):
    model = CompetenceEdge


class CompetenceEdgeCreate(MapEntityCreate):
    model = CompetenceEdge
    form_class = CompetenceEdgeForm


class CompetenceEdgeUpdate(MapEntityUpdate):
    queryset = CompetenceEdge.objects.existing()
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
    fields = ['color_index', 'name']


class WorkManagementEdgeList(MapEntityList):
    queryset = WorkManagementEdge.objects.existing()
    filterform = WorkManagementEdgeFilter
    columns = ['id', 'organization']


class WorkManagementEdgeJsonList(MapEntityJsonList, WorkManagementEdgeList):
    pass


class WorkManagementEdgeFormatList(MapEntityFormat, WorkManagementEdgeList):
    pass


class WorkManagementEdgeDetail(MapEntityDetail):
    queryset = WorkManagementEdge.objects.existing()

    def can_edit(self):
        return self.request.user.is_superuser or \
               (hasattr(self.request.user, 'profile') and \
                self.request.user.profile.is_path_manager)


class WorkManagementEdgeDocument(MapEntityDocument):
    model = WorkManagementEdge


class WorkManagementEdgeCreate(MapEntityCreate):
    model = WorkManagementEdge
    form_class = WorkManagementEdgeForm


class WorkManagementEdgeUpdate(MapEntityUpdate):
    queryset = WorkManagementEdge.objects.existing()
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
    fields = ['color_index', 'name']


class SignageManagementEdgeList(MapEntityList):
    queryset = SignageManagementEdge.objects.existing()
    filterform = SignageManagementEdgeFilter
    columns = ['id', 'organization']


class SignageManagementEdgeJsonList(MapEntityJsonList, SignageManagementEdgeList):
    pass


class SignageManagementEdgeFormatList(MapEntityFormat, SignageManagementEdgeList):
    pass


class SignageManagementEdgeDetail(MapEntityDetail):
    queryset = SignageManagementEdge.objects.existing()

    def can_edit(self):
        return self.request.user.is_superuser or \
               (hasattr(self.request.user, 'profile') and \
                self.request.user.profile.is_path_manager)


class SignageManagementEdgeDocument(MapEntityDocument):
    model = SignageManagementEdge


class SignageManagementEdgeCreate(MapEntityCreate):
    model = SignageManagementEdge
    form_class = SignageManagementEdgeForm


class SignageManagementEdgeUpdate(MapEntityUpdate):
    queryset = SignageManagementEdge.objects.existing()
    form_class = SignageManagementEdgeForm

    @method_decorator(path_manager_required('land:signagemanagementedge_detail'))
    def dispatch(self, *args, **kwargs):
        return super(SignageManagementEdgeUpdate, self).dispatch(*args, **kwargs)


class SignageManagementEdgeDelete(MapEntityDelete):
    model = SignageManagementEdge

    @method_decorator(path_manager_required('land:signagemanagementedge_detail'))
    def dispatch(self, *args, **kwargs):
        return super(SignageManagementEdgeDelete, self).dispatch(*args, **kwargs)
