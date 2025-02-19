from django.conf import settings
from django.contrib.gis.db.models.functions import Transform
from django.db.models.query import Prefetch
from mapentity.views import (
    MapEntityCreate,
    MapEntityDelete,
    MapEntityDetail,
    MapEntityDocument,
    MapEntityFormat,
    MapEntityList,
    MapEntityFilter,
    MapEntityUpdate,
)

from geotrek.authent.decorators import same_structure_required
from geotrek.common.mixins.views import CustomColumnsMixin
from geotrek.common.viewsets import GeotrekMapentityViewSet
from geotrek.core.models import AltimetryMixin
from geotrek.core.views import CreateFromTopologyMixin

from .filters import InfrastructureFilterSet
from .forms import InfrastructureForm
from .models import Infrastructure, InfrastructureCondition
from .serializers import InfrastructureGeojsonSerializer, InfrastructureSerializer


class InfrastructureList(CustomColumnsMixin, MapEntityList):
    queryset = Infrastructure.objects.existing()
    mandatory_columns = ['id', 'name']
    default_extra_columns = ['type', 'conditions', 'cities']
    searchable_columns = ['id', 'name']


class InfrastructureFilter(MapEntityFilter):
    model = Infrastructure
    filterset_class = InfrastructureFilterSet


class InfrastructureFormatList(MapEntityFormat, InfrastructureList):
    filterset_class = InfrastructureFilterSet
    mandatory_columns = ['id']
    default_extra_columns = [
        'id', 'name', 'type', 'conditions', 'description', 'accessibility',
        'implantation_year', 'published', 'publication_date', 'structure', 'date_insert',
        'date_update', 'cities', 'districts', 'areas', 'usage_difficulty',
        'maintenance_difficulty', 'access', 'uuid',
    ] + AltimetryMixin.COLUMNS


class InfrastructureDetail(MapEntityDetail):
    queryset = Infrastructure.objects.existing()

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['can_edit'] = self.get_object().same_structure(self.request.user)
        return context


class InfrastructureDocument(MapEntityDocument):
    model = Infrastructure


class InfrastructureCreate(CreateFromTopologyMixin, MapEntityCreate):
    model = Infrastructure
    form_class = InfrastructureForm


class InfrastructureUpdate(MapEntityUpdate):
    queryset = Infrastructure.objects.existing()
    form_class = InfrastructureForm

    @same_structure_required('infrastructure:infrastructure_detail')
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class InfrastructureDelete(MapEntityDelete):
    model = Infrastructure

    @same_structure_required('infrastructure:infrastructure_detail')
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class InfrastructureViewSet(GeotrekMapentityViewSet):
    model = Infrastructure
    serializer_class = InfrastructureSerializer
    geojson_serializer_class = InfrastructureGeojsonSerializer
    filterset_class = InfrastructureFilterSet
    mapentity_list_class = InfrastructureList

    def get_queryset(self):
        qs = self.model.objects.existing()
        if self.format_kwarg == 'geojson':
            qs = qs.annotate(api_geom=Transform('geom', settings.API_SRID))
            qs = qs.only('id', 'name', 'published')
        else:
            qs = qs.select_related('type', 'maintenance_difficulty', 'access', 'usage_difficulty').prefetch_related(
                Prefetch('conditions',
                         queryset=InfrastructureCondition.objects.select_related('structure'), to_attr="conditions_list"),)
        return qs
