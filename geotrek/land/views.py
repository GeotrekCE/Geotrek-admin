from django.conf import settings
from django.contrib.gis.db.models.functions import Transform
from mapentity.views import (MapEntityList, MapEntityFormat, MapEntityFilter, MapEntityDetail, MapEntityDocument,
                             MapEntityCreate, MapEntityUpdate, MapEntityDelete)

from geotrek.common.mixins.views import CustomColumnsMixin
from geotrek.common.viewsets import GeotrekMapentityViewSet
from geotrek.core.models import AltimetryMixin
from geotrek.core.views import CreateFromTopologyMixin
from .filters import PhysicalEdgeFilterSet, LandEdgeFilterSet, CompetenceEdgeFilterSet, WorkManagementEdgeFilterSet, \
    SignageManagementEdgeFilterSet, CirculationEdgeFilterSet
from .forms import PhysicalEdgeForm, LandEdgeForm, CompetenceEdgeForm, WorkManagementEdgeForm, SignageManagementEdgeForm, \
    CirculationEdgeForm
from .models import (PhysicalEdge, LandEdge, CompetenceEdge,
                     WorkManagementEdge, SignageManagementEdge,
                     CirculationEdge)
from .serializers import LandEdgeSerializer, PhysicalEdgeSerializer, CompetenceEdgeSerializer, \
    SignageManagementEdgeSerializer, WorkManagementEdgeSerializer, PhysicalEdgeGeojsonSerializer, \
    LandEdgeGeojsonSerializer, CompetenceEdgeGeojsonSerializer, WorkManagementEdgeGeojsonSerializer, \
    SignageManagementEdgeGeojsonSerializer, CirculationEdgeSerializer, CirculationEdgeGeojsonSerializer


class PhysicalEdgeList(CustomColumnsMixin, CreateFromTopologyMixin, MapEntityList):
    queryset = PhysicalEdge.objects.existing()
    mandatory_columns = ['id', 'physical_type']
    default_extra_columns = ['length', 'length_2d']


class PhysicalEdgeFilter(MapEntityFilter):
    model = PhysicalEdge
    filterset_class = PhysicalEdgeFilterSet


class PhysicalEdgeFormatList(MapEntityFormat, PhysicalEdgeList):
    filterset_class = PhysicalEdgeFilterSet
    mandatory_columns = ['id', 'physical_type']
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
    mandatory_columns = ['id', 'land_type']
    default_extra_columns = ['length', 'length_2d']


class LandEdgeFilter(MapEntityFilter):
    model = LandEdge
    filterset_class = LandEdgeFilterSet


class LandEdgeFormatList(MapEntityFormat, LandEdgeList):
    filterset_class = LandEdgeFilterSet
    mandatory_columns = ['id']
    default_extra_columns = [
        'land_type', 'owner', 'agreement', 'date_insert', 'date_update',
        'cities', 'districts', 'areas', 'uuid', 'length_2d'
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


class CirculationEdgeList(CustomColumnsMixin, MapEntityList):
    queryset = CirculationEdge.objects.existing()
    mandatory_columns = ['id', 'circulation_type', 'authorization_type']
    default_extra_columns = ['length', 'length_2d']


class CirculationEdgeFilter(MapEntityFilter):
    model = CirculationEdge
    filterset_class = CirculationEdgeFilterSet


class CirculationEdgeFormatList(MapEntityFormat, CirculationEdgeList):
    filterset_class = CirculationEdgeFilterSet
    mandatory_columns = ['id']
    default_extra_columns = [
        'circulation_type', 'authorization_type', 'date_insert', 'date_update',
        'cities', 'districts', 'areas', 'uuid', 'length_2d'
    ] + AltimetryMixin.COLUMNS


class CirculationEdgeDetail(MapEntityDetail):
    queryset = CirculationEdge.objects.existing()


class CirculationEdgeDocument(MapEntityDocument):
    model = CirculationEdge


class CirculationEdgeCreate(CreateFromTopologyMixin, MapEntityCreate):
    model = CirculationEdge
    form_class = CirculationEdgeForm


class CirculationEdgeUpdate(MapEntityUpdate):
    queryset = CirculationEdge.objects.existing()
    form_class = CirculationEdgeForm


class CirculationEdgeDelete(MapEntityDelete):
    model = CirculationEdge


class CirculationEdgeViewSet(GeotrekMapentityViewSet):
    model = CirculationEdge
    serializer_class = CirculationEdgeSerializer
    geojson_serializer_class = CirculationEdgeGeojsonSerializer
    filterset_class = CirculationEdgeFilterSet
    mapentity_list_class = CirculationEdgeList

    def get_queryset(self):
        qs = self.model.objects.existing().select_related('circulation_type')
        if self.format_kwarg == 'geojson':
            qs = qs.annotate(api_geom=Transform('geom', settings.API_SRID))
            qs = qs.only('id', 'circulation_type')
            return qs
        return qs.defer('geom', 'geom_3d')


class CompetenceEdgeList(CustomColumnsMixin, MapEntityList):
    queryset = CompetenceEdge.objects.existing()
    mandatory_columns = ['id', 'organization']
    default_extra_columns = ['length', 'length_2d']


class CompetenceEdgeFilter(MapEntityFilter):
    model = CompetenceEdge
    filterset_class = CompetenceEdgeFilterSet


class CompetenceEdgeFormatList(MapEntityFormat, CompetenceEdgeList):
    filterset_class = CompetenceEdgeFilterSet
    mandatory_columns = ['id', 'organization']
    default_extra_columns = [
        'date_insert', 'date_update',
        'cities', 'districts', 'areas', 'uuid', 'length_2d'
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
    mandatory_columns = ['id', 'organization']
    default_extra_columns = ['length', 'length_2d']


class WorkManagementEdgeFilter(MapEntityFilter):
    model = WorkManagementEdge
    filterset_class = WorkManagementEdgeFilterSet


class WorkManagementEdgeFormatList(MapEntityFormat, WorkManagementEdgeList):
    filterset_class = WorkManagementEdgeFilterSet
    mandatory_columns = ['id', 'organization']
    default_extra_columns = [
        'date_insert', 'date_update', 'cities', 'districts', 'areas', 'uuid', 'length_2d'
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
    mandatory_columns = ['id', 'organization']
    default_extra_columns = ['length', 'length_2d']


class SignageManagementEdgeFilter(MapEntityFilter):
    model = SignageManagementEdge
    filterset_class = SignageManagementEdgeFilterSet


class SignageManagementEdgeFormatList(MapEntityFormat, SignageManagementEdgeList):
    filterset_class = SignageManagementEdgeFilterSet
    mandatory_columns = ['id', 'organization']
    default_extra_columns = [
        'date_insert', 'date_update', 'cities', 'districts', 'areas', 'uuid', 'length_2d'
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
