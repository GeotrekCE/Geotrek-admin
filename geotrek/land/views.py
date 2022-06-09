from django.conf import settings
from mapentity.views import (MapEntityLayer, MapEntityList, MapEntityFormat, MapEntityDetail, MapEntityDocument,
                             MapEntityCreate, MapEntityUpdate, MapEntityDelete)
from geotrek.common.mixins.views import CustomColumnsMixin
from geotrek.core.models import AltimetryMixin
from geotrek.core.views import CreateFromTopologyMixin
from .models import (PhysicalEdge, LandEdge, CompetenceEdge,
                     WorkManagementEdge, SignageManagementEdge)
from .filters import PhysicalEdgeFilterSet, LandEdgeFilterSet, CompetenceEdgeFilterSet, WorkManagementEdgeFilterSet, SignageManagementEdgeFilterSet
from .forms import PhysicalEdgeForm, LandEdgeForm, CompetenceEdgeForm, WorkManagementEdgeForm, SignageManagementEdgeForm
from .serializers import LandEdgeSerializer, PhysicalEdgeSerializer, CompetenceEdgeSerializer, \
    SignageManagementEdgeSerializer, WorkManagementEdgeSerializer
from ..common.viewsets import GeotrekMapentityViewSet


class PhysicalEdgeLayer(MapEntityLayer):
    queryset = PhysicalEdge.objects.existing()
    properties = ['color_index', 'name']


class PhysicalEdgeList(CustomColumnsMixin, CreateFromTopologyMixin, MapEntityList):
    queryset = PhysicalEdge.objects.existing()
    filterform = PhysicalEdgeFilterSet
    mandatory_columns = ['id', 'physical_type']
    default_extra_columns = ['length']


class PhysicalEdgeFormatList(MapEntityFormat, PhysicalEdgeList):
    default_extra_columns = [
        'date_insert', 'date_update',
        'cities', 'districts', 'areas', 'uuid',
    ] + AltimetryMixin.COLUMNS


class PhysicalEdgeDetail(MapEntityDetail):
    queryset = PhysicalEdge.objects.existing()


class PhysicalEdgeDocument(MapEntityDocument):
    model = PhysicalEdge


class PhysicalEdgeCreate(CreateFromTopologyMixin, MapEntityCreate):
    model = PhysicalEdge
    form_class = PhysicalEdgeForm


class PhysicalEdgeUpdate(MapEntityUpdate):
    queryset = PhysicalEdge.objects.existing()
    form_class = PhysicalEdgeForm


class PhysicalEdgeDelete(MapEntityDelete):
    model = PhysicalEdge


class PhysicalEdgeViewSet(GeotrekMapentityViewSet):
    model = PhysicalEdge
    serializer_class = PhysicalEdgeSerializer
    filterset_class = PhysicalEdgeFilterSet

    def get_columns(self):
        return PhysicalEdgeList.mandatory_columns + settings.COLUMNS_LISTS.get('physicaledge_view',
                                                                               PhysicalEdgeList.default_extra_columns)

    def get_queryset(self):
        return PhysicalEdge.objects.existing().select_related('physical_type').defer('geom', 'geom_3d')


class LandEdgeLayer(MapEntityLayer):
    queryset = LandEdge.objects.existing()
    properties = ['color_index', 'name']


class LandEdgeList(CustomColumnsMixin, MapEntityList):
    queryset = LandEdge.objects.existing()
    filterform = LandEdgeFilterSet
    mandatory_columns = ['id', 'land_type']
    default_extra_columns = ['length']


class LandEdgeFormatList(MapEntityFormat, LandEdgeList):
    mandatory_columns = ['id']
    default_extra_columns = [
        'land_type', 'owner', 'agreement',
        'date_insert', 'date_update',
        'cities', 'districts', 'areas', 'uuid',
    ] + AltimetryMixin.COLUMNS


class LandEdgeDetail(MapEntityDetail):
    queryset = LandEdge.objects.existing()


class LandEdgeDocument(MapEntityDocument):
    model = LandEdge


class LandEdgeCreate(CreateFromTopologyMixin, MapEntityCreate):
    model = LandEdge
    form_class = LandEdgeForm


class LandEdgeUpdate(MapEntityUpdate):
    queryset = LandEdge.objects.existing()
    form_class = LandEdgeForm


class LandEdgeDelete(MapEntityDelete):
    model = LandEdge


class LandEdgeViewSet(GeotrekMapentityViewSet):
    model = LandEdge
    serializer_class = LandEdgeSerializer
    filterset_class = LandEdgeFilterSet

    def get_columns(self):
        return LandEdgeList.mandatory_columns + settings.COLUMNS_LISTS.get('landedge_view',
                                                                           LandEdgeList.default_extra_columns)

    def get_queryset(self):
        return LandEdge.objects.existing().select_related('land_type').defer('geom', 'geom_3d')


class CompetenceEdgeLayer(MapEntityLayer):
    queryset = CompetenceEdge.objects.existing()
    properties = ['color_index', 'name']


class CompetenceEdgeList(CustomColumnsMixin, MapEntityList):
    queryset = CompetenceEdge.objects.existing()
    filterform = CompetenceEdgeFilterSet
    mandatory_columns = ['id', 'organization']
    default_extra_columns = ['length']


class CompetenceEdgeFormatList(MapEntityFormat, CompetenceEdgeList):
    default_extra_columns = [
        'date_insert', 'date_update',
        'cities', 'districts', 'areas', 'uuid',
    ] + AltimetryMixin.COLUMNS


class CompetenceEdgeDetail(MapEntityDetail):
    queryset = CompetenceEdge.objects.existing()


class CompetenceEdgeDocument(MapEntityDocument):
    model = CompetenceEdge


class CompetenceEdgeCreate(CreateFromTopologyMixin, MapEntityCreate):
    model = CompetenceEdge
    form_class = CompetenceEdgeForm


class CompetenceEdgeUpdate(MapEntityUpdate):
    queryset = CompetenceEdge.objects.existing()
    form_class = CompetenceEdgeForm


class CompetenceEdgeDelete(MapEntityDelete):
    model = CompetenceEdge


class CompetenceEdgeViewSet(GeotrekMapentityViewSet):
    model = CompetenceEdge
    serializer_class = CompetenceEdgeSerializer
    filterset_class = CompetenceEdgeFilterSet

    def get_columns(self):
        return CompetenceEdgeList.mandatory_columns + settings.COLUMNS_LISTS.get('competenceedge_view',
                                                                                 CompetenceEdgeList.default_extra_columns)

    def get_queryset(self):
        return CompetenceEdge.objects.existing().select_related('organization').defer('geom', 'geom_3d')


class WorkManagementEdgeLayer(MapEntityLayer):
    queryset = WorkManagementEdge.objects.existing()
    properties = ['color_index', 'name']


class WorkManagementEdgeList(CustomColumnsMixin, MapEntityList):
    queryset = WorkManagementEdge.objects.existing()
    filterform = WorkManagementEdgeFilterSet
    mandatory_columns = ['id', 'organization']
    default_extra_columns = ['length']


class WorkManagementEdgeFormatList(MapEntityFormat, WorkManagementEdgeList):
    default_extra_columns = [
        'date_insert', 'date_update',
        'cities', 'districts', 'areas', 'uuid',
    ] + AltimetryMixin.COLUMNS


class WorkManagementEdgeDetail(MapEntityDetail):
    queryset = WorkManagementEdge.objects.existing()


class WorkManagementEdgeDocument(MapEntityDocument):
    model = WorkManagementEdge


class WorkManagementEdgeCreate(CreateFromTopologyMixin, MapEntityCreate):
    model = WorkManagementEdge
    form_class = WorkManagementEdgeForm


class WorkManagementEdgeUpdate(MapEntityUpdate):
    queryset = WorkManagementEdge.objects.existing()
    form_class = WorkManagementEdgeForm


class WorkManagementEdgeDelete(MapEntityDelete):
    model = WorkManagementEdge


class WorkManagementEdgeViewSet(GeotrekMapentityViewSet):
    model = WorkManagementEdge
    serializer_class = WorkManagementEdgeSerializer
    filterset_class = WorkManagementEdgeFilterSet

    def get_columns(self):
        return WorkManagementEdgeList.mandatory_columns + settings.COLUMNS_LISTS.get('workmanagementedge_view',
                                                                                     WorkManagementEdgeList.default_extra_columns)

    def get_queryset(self):
        return WorkManagementEdge.objects.existing().select_related('organization').defer('geom', 'geom_3d')


class SignageManagementEdgeLayer(MapEntityLayer):
    queryset = SignageManagementEdge.objects.existing()
    properties = ['color_index', 'name']


class SignageManagementEdgeList(CustomColumnsMixin, MapEntityList):
    queryset = SignageManagementEdge.objects.existing()
    filterform = SignageManagementEdgeFilterSet
    mandatory_columns = ['id', 'organization']
    default_extra_columns = ['length']


class SignageManagementEdgeFormatList(MapEntityFormat, SignageManagementEdgeList):
    default_extra_columns = [
        'date_insert', 'date_update',
        'cities', 'districts', 'areas', 'uuid',
    ] + AltimetryMixin.COLUMNS


class SignageManagementEdgeDetail(MapEntityDetail):
    queryset = SignageManagementEdge.objects.existing()


class SignageManagementEdgeDocument(MapEntityDocument):
    model = SignageManagementEdge


class SignageManagementEdgeCreate(CreateFromTopologyMixin, MapEntityCreate):
    model = SignageManagementEdge
    form_class = SignageManagementEdgeForm


class SignageManagementEdgeUpdate(MapEntityUpdate):
    queryset = SignageManagementEdge.objects.existing()
    form_class = SignageManagementEdgeForm


class SignageManagementEdgeDelete(MapEntityDelete):
    model = SignageManagementEdge


class SignageManagementEdgeViewSet(GeotrekMapentityViewSet):
    model = SignageManagementEdge
    serializer_class = SignageManagementEdgeSerializer
    filterset_class = SignageManagementEdgeFilterSet

    def get_columns(self):
        return SignageManagementEdgeList.mandatory_columns + settings.COLUMNS_LISTS.get('competenceedge_view',
                                                                                        SignageManagementEdgeList.default_extra_columns)

    def get_queryset(self):
        return SignageManagementEdge.objects.existing().select_related('organization').defer('geom', 'geom_3d')
