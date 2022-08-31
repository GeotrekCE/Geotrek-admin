from django.conf import settings
from django.contrib.gis.db.models.functions import Transform
from mapentity.views import (MapEntityList, MapEntityFormat, MapEntityDetail, MapEntityDocument,
                             MapEntityCreate, MapEntityUpdate, MapEntityDelete)

from geotrek.common.mixins.views import CustomColumnsMixin, DuplicateDetailMixin, DuplicateMixin
from geotrek.common.viewsets import GeotrekMapentityViewSet
from geotrek.core.models import AltimetryMixin
from geotrek.core.views import CreateFromTopologyMixin
from .filters import PhysicalEdgeFilterSet, LandEdgeFilterSet, CompetenceEdgeFilterSet, WorkManagementEdgeFilterSet, \
    SignageManagementEdgeFilterSet
from .forms import PhysicalEdgeForm, LandEdgeForm, CompetenceEdgeForm, WorkManagementEdgeForm, SignageManagementEdgeForm
from .models import (PhysicalEdge, LandEdge, CompetenceEdge,
                     WorkManagementEdge, SignageManagementEdge)
from .serializers import LandEdgeSerializer, PhysicalEdgeSerializer, CompetenceEdgeSerializer, \
    SignageManagementEdgeSerializer, WorkManagementEdgeSerializer, PhysicalEdgeGeojsonSerializer, \
    LandEdgeGeojsonSerializer, CompetenceEdgeGeojsonSerializer, WorkManagementEdgeGeojsonSerializer, \
    SignageManagementEdgeGeojsonSerializer


class PhysicalEdgeList(CustomColumnsMixin, CreateFromTopologyMixin, MapEntityList):
    queryset = PhysicalEdge.objects.existing()
    filterform = PhysicalEdgeFilterSet
    mandatory_columns = ['id', 'physical_type']
    default_extra_columns = ['length', 'length_2d']


class PhysicalEdgeFormatList(MapEntityFormat, PhysicalEdgeList):
    mandatory_columns = ['id', 'physical_type']
    default_extra_columns = [
        'date_insert', 'date_update',
        'cities', 'districts', 'areas', 'uuid',
    ] + AltimetryMixin.COLUMNS


class PhysicalEdgeDetail(DuplicateDetailMixin, MapEntityDetail):
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


class PhysicalEdgeViewSet(DuplicateMixin, GeotrekMapentityViewSet):
    model = PhysicalEdge
    serializer_class = PhysicalEdgeSerializer
    geojson_serializer_class = PhysicalEdgeGeojsonSerializer
    filterset_class = PhysicalEdgeFilterSet
    mapentity_list_class = PhysicalEdgeList

    def get_queryset(self):
        qs = self.model.objects.existing().select_related('physical_type')

        if self.format_kwarg == 'geojson':
            qs = qs.annotate(api_geom=Transform('geom', settings.API_SRID))
            qs = qs.only('id', 'physical_type')
            return qs

        return qs.defer('geom', 'geom_3d')


class LandEdgeList(CustomColumnsMixin, MapEntityList):
    queryset = LandEdge.objects.existing()
    filterform = LandEdgeFilterSet
    mandatory_columns = ['id', 'land_type']
    default_extra_columns = ['length', 'length_2d']


class LandEdgeFormatList(MapEntityFormat, LandEdgeList):
    mandatory_columns = ['id']
    default_extra_columns = [
        'land_type', 'owner', 'agreement', 'date_insert', 'date_update',
        'cities', 'districts', 'areas', 'uuid', 'length_2d'
    ] + AltimetryMixin.COLUMNS


class LandEdgeDetail(DuplicateDetailMixin, MapEntityDetail):
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


class LandEdgeViewSet(DuplicateMixin, GeotrekMapentityViewSet):
    model = LandEdge
    serializer_class = LandEdgeSerializer
    geojson_serializer_class = LandEdgeGeojsonSerializer
    filterset_class = LandEdgeFilterSet
    mapentity_list_class = LandEdgeList

    def get_queryset(self):
        qs = self.model.objects.existing().select_related('land_type')
        if self.format_kwarg == 'geojson':
            qs = qs.annotate(api_geom=Transform('geom', settings.API_SRID))
            qs = qs.only('id', 'land_type')
            return qs
        return qs.defer('geom', 'geom_3d')


class CompetenceEdgeList(CustomColumnsMixin, MapEntityList):
    queryset = CompetenceEdge.objects.existing()
    filterform = CompetenceEdgeFilterSet
    mandatory_columns = ['id', 'organization']
    default_extra_columns = ['length', 'length_2d']


class CompetenceEdgeFormatList(MapEntityFormat, CompetenceEdgeList):
    mandatory_columns = ['id', 'organization']
    default_extra_columns = [
        'date_insert', 'date_update',
        'cities', 'districts', 'areas', 'uuid', 'length_2d'
    ] + AltimetryMixin.COLUMNS


class CompetenceEdgeDetail(DuplicateDetailMixin, MapEntityDetail):
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


class CompetenceEdgeViewSet(DuplicateMixin, GeotrekMapentityViewSet):
    model = CompetenceEdge
    serializer_class = CompetenceEdgeSerializer
    geojson_serializer_class = CompetenceEdgeGeojsonSerializer
    filterset_class = CompetenceEdgeFilterSet
    mapentity_list_class = CompetenceEdgeList

    def get_queryset(self):
        qs = self.model.objects.existing().select_related('organization')
        if self.format_kwarg == 'geojson':
            qs = qs.annotate(api_geom=Transform('geom', settings.API_SRID))
            qs = qs.only('id', 'organization')
            return qs
        return qs.defer('geom', 'geom_3d')


class WorkManagementEdgeList(CustomColumnsMixin, MapEntityList):
    queryset = WorkManagementEdge.objects.existing()
    filterform = WorkManagementEdgeFilterSet
    mandatory_columns = ['id', 'organization']
    default_extra_columns = ['length', 'length_2d']


class WorkManagementEdgeFormatList(MapEntityFormat, WorkManagementEdgeList):
    mandatory_columns = ['id', 'organization']
    default_extra_columns = [
        'date_insert', 'date_update', 'cities', 'districts', 'areas', 'uuid', 'length_2d'
    ] + AltimetryMixin.COLUMNS


class WorkManagementEdgeDetail(DuplicateDetailMixin, MapEntityDetail):
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


class WorkManagementEdgeViewSet(DuplicateMixin, GeotrekMapentityViewSet):
    model = WorkManagementEdge
    serializer_class = WorkManagementEdgeSerializer
    geojson_serializer_class = WorkManagementEdgeGeojsonSerializer
    filterset_class = WorkManagementEdgeFilterSet
    mapentity_list_class = WorkManagementEdgeList

    def get_queryset(self):
        qs = self.model.objects.existing().select_related('organization')
        if self.format_kwarg == 'geojson':
            qs = qs.annotate(api_geom=Transform('geom', settings.API_SRID))
            qs = qs.only('id', 'organization')
            return qs
        return qs.defer('geom', 'geom_3d')


class SignageManagementEdgeList(CustomColumnsMixin, MapEntityList):
    queryset = SignageManagementEdge.objects.existing()
    filterform = SignageManagementEdgeFilterSet
    mandatory_columns = ['id', 'organization']
    default_extra_columns = ['length', 'length_2d']


class SignageManagementEdgeFormatList(MapEntityFormat, SignageManagementEdgeList):
    mandatory_columns = ['id', 'organization']
    default_extra_columns = [
        'date_insert', 'date_update', 'cities', 'districts', 'areas', 'uuid', 'length_2d'
    ] + AltimetryMixin.COLUMNS


class SignageManagementEdgeDetail(DuplicateDetailMixin, MapEntityDetail):
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


class SignageManagementEdgeViewSet(DuplicateMixin, GeotrekMapentityViewSet):
    model = SignageManagementEdge
    serializer_class = SignageManagementEdgeSerializer
    geojson_serializer_class = SignageManagementEdgeGeojsonSerializer
    filterset_class = SignageManagementEdgeFilterSet
    mapentity_list_class = SignageManagementEdgeList

    def get_queryset(self):
        qs = self.model.objects.existing().select_related('organization')
        if self.format_kwarg == 'geojson':
            qs = qs.annotate(api_geom=Transform('geom', settings.API_SRID))
            qs = qs.only('id', 'organization')
            return qs
        return qs.defer('geom', 'geom_3d')
