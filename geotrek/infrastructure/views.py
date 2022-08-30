from django.conf import settings
from django.contrib.gis.db.models.functions import Transform
from mapentity.views import (MapEntityList, MapEntityFormat, MapEntityDetail, MapEntityDocument,
                             MapEntityCreate, MapEntityUpdate, MapEntityDelete)

from geotrek.authent.decorators import same_structure_required
from geotrek.common.mixins.api import APIViewSet
from geotrek.common.mixins.views import CustomColumnsMixin, DuplicateMixin, DuplicateDetailMixin
from geotrek.common.viewsets import GeotrekMapentityViewSet
from geotrek.core.models import AltimetryMixin
from geotrek.core.views import CreateFromTopologyMixin
from .filters import InfrastructureFilterSet
from .forms import InfrastructureForm
from .models import Infrastructure
from .serializers import InfrastructureSerializer, InfrastructureAPIGeojsonSerializer, InfrastructureAPISerializer, \
    InfrastructureGeojsonSerializer


class InfrastructureList(CustomColumnsMixin, MapEntityList):
    queryset = Infrastructure.objects.existing()
    filterform = InfrastructureFilterSet
    mandatory_columns = ['id', 'checkbox', 'name']
    default_extra_columns = ['type', 'condition', 'cities']
    searchable_columns = ['id', 'name']
    unorderable_columns = ['checkbox']


class InfrastructureFormatList(MapEntityFormat, InfrastructureList):
    mandatory_columns = ['id']
    default_extra_columns = [
        'id', 'name', 'type', 'condition', 'description', 'accessibility',
        'implantation_year', 'published', 'publication_date', 'structure', 'date_insert',
        'date_update', 'cities', 'districts', 'areas', 'usage_difficulty', 'maintenance_difficulty', 'uuid',
    ] + AltimetryMixin.COLUMNS


class InfrastructureDetail(DuplicateDetailMixin, MapEntityDetail):
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


class InfrastructureViewSet(DuplicateMixin, GeotrekMapentityViewSet):
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
            qs = qs.select_related('type', 'maintenance_difficulty', 'usage_difficulty')
        return qs


class InfrastructureAPIViewSet(APIViewSet):
    model = Infrastructure
    serializer_class = InfrastructureAPISerializer
    geojson_serializer_class = InfrastructureAPIGeojsonSerializer

    def get_queryset(self):
        return Infrastructure.objects.existing().filter(published=True).annotate(api_geom=Transform("geom", settings.API_SRID))
