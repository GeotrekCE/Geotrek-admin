import logging

from django.conf import settings
from django.contrib.gis.db.models.functions import Transform
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from mapentity.renderers import GeoJSONRenderer
from mapentity.views import (MapEntityLayer, MapEntityList, MapEntityFormat, MapEntityDetail,
                             MapEntityDocument, MapEntityCreate, MapEntityUpdate, MapEntityDelete)
from rest_framework import permissions as rest_permissions, renderers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_datatables.filters import DatatablesFilterBackend

from geotrek.authent.decorators import same_structure_required
from geotrek.common.mixins.views import CustomColumnsMixin
from geotrek.common.views import FormsetMixin
from geotrek.common.viewsets import GeotrekMapentityViewSet
from geotrek.core.models import AltimetryMixin
from geotrek.signage.filters import SignageFilterSet, BladeFilterSet
from geotrek.signage.forms import SignageForm, BladeForm, LineFormset
from geotrek.signage.models import Signage, Blade
from geotrek.signage.serializers import (SignageSerializer, BladeSerializer,
                                         SignageRandoV2GeojsonSerializer, CSVBladeSerializer, ZipBladeShapeSerializer)

logger = logging.getLogger(__name__)


class LineMixin(FormsetMixin):
    context_name = 'line_formset'
    formset_class = LineFormset


class SignageLayer(MapEntityLayer):
    queryset = Signage.objects.existing()
    properties = ['name', 'published']


class SignageList(CustomColumnsMixin, MapEntityList):
    queryset = Signage.objects.existing()
    filterform = SignageFilterSet
    mandatory_columns = ['id', 'name']
    default_extra_columns = ['code', 'type', 'condition']


class SignageFormatList(MapEntityFormat, SignageList):
    mandatory_columns = ['id']
    default_extra_columns = [
        'structure', 'name', 'code', 'type', 'condition', 'description',
        'implantation_year', 'published', 'date_insert',
        'date_update', 'cities', 'districts', 'areas', 'lat_value', 'lng_value',
        'printed_elevation', 'sealing', 'manager', 'uuid',
    ] + AltimetryMixin.COLUMNS


class SignageDetail(MapEntityDetail):
    queryset = Signage.objects.existing()

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['can_edit'] = self.get_object().same_structure(self.request.user)
        return context


class SignageDocument(MapEntityDocument):
    model = Signage


class SignageCreate(MapEntityCreate):
    model = Signage
    form_class = SignageForm


class SignageUpdate(MapEntityUpdate):
    queryset = Signage.objects.existing()
    form_class = SignageForm

    @same_structure_required('signage:signage_detail')
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class SignageDelete(MapEntityDelete):
    model = Signage

    @same_structure_required('signage:signage_detail')
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class SignageViewSet(GeotrekMapentityViewSet):
    model = Signage
    serializer_class = SignageSerializer
    filterset_class = SignageFilterSet

    def get_queryset(self):
        qs = Signage.objects.existing().select_related('structure', 'manager', 'sealing', 'type', 'condition')
        if self.action != 'rando-v2-geojson':
            qs = qs.defer('geom', 'geom_3d')
        else:
            qs = qs.filter(published=True).annotate(api_geom=Transform("geom", settings.API_SRID))
        return qs

    def get_columns(self):
        return SignageList.mandatory_columns + settings.COLUMNS_LISTS.get('signage_view',
                                                                          SignageList.default_extra_columns)

    @action(methods=['GET'], detail=False, renderer_classes=[renderers.BrowsableAPIRenderer, GeoJSONRenderer],
            serializer_class=SignageRandoV2GeojsonSerializer)
    def rando_v2_geojson(self, request, lang=None):
        """ GeoJSON for RandoV2. """
        qs = self.get_queryset()
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)


class BladeDetail(MapEntityDetail):
    queryset = Blade.objects.all()

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['can_edit'] = self.get_object().signage.same_structure(self.request.user)
        return context


class BladeDocument(MapEntityDocument):
    model = Blade


class BladeCreate(LineMixin, MapEntityCreate):
    model = Blade
    form_class = BladeForm

    def get_signage(self):
        pk_infra = self.request.GET.get('signage')
        if pk_infra:
            try:
                return Signage.objects.existing().get(pk=pk_infra)
            except Signage.DoesNotExist:
                logger.warning("Intervention on unknown infrastructure %s" % pk_infra)
        return None

    def get_initial(self):
        """
        Returns the initial data to use for forms on this view.
        """
        initial = super().get_initial()
        signage = self.get_signage()
        initial['signage'] = signage
        return initial

    def get_success_url(self):
        return self.get_signage().get_detail_url()


class BladeUpdate(LineMixin, MapEntityUpdate):
    queryset = Blade.objects.all()
    form_class = BladeForm

    @same_structure_required('signage:blade_detail')
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class BladeDelete(MapEntityDelete):
    model = Blade

    @same_structure_required('signage:blade_detail')
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def delete(self, request, *args, **kwargs):
        self.signage = self.get_object().signage
        return super().delete(request, args, kwargs)

    def get_success_url(self):
        return self.signage.get_detail_url()


class BladeViewSet(GeotrekMapentityViewSet):
    model = Blade
    serializer_class = BladeSerializer
    filterset_class = BladeFilterSet
    filter_backends = [DatatablesFilterBackend, DjangoFilterBackend]  #TODO : fix filter topology
    permission_classes = [rest_permissions.DjangoModelPermissionsOrAnonReadOnly]

    def get_queryset(self):
        return self.model.objects.all()


class BladeList(CustomColumnsMixin, MapEntityList):
    queryset = Blade.objects.all()
    filterform = BladeFilterSet
    mandatory_columns = ['id', 'number']
    default_extra_columns = ['direction', 'type', 'color']


class BladeLayer(MapEntityLayer):
    queryset = Blade.objects.all()
    properties = ['number']


class BladeFormatList(MapEntityFormat, BladeList):
    mandatory_columns = ['id']
    default_extra_columns = ['city', 'signage', 'printedelevation', 'bladecode', 'type', 'color', 'direction',
                             'condition', 'coordinates']
    columns_line = ['number', 'text', 'distance_pretty', 'time_pretty', 'pictogram_name']

    def csv_view(self, request, context, **kwargs):
        serializer = CSVBladeSerializer()
        response = HttpResponse(content_type='text/csv')
        serializer.serialize(queryset=self.get_queryset(), stream=response,
                             model=self.get_model(), fields=self.columns, line_fields=self.columns_line,
                             ensure_ascii=True)
        return response

    def shape_view(self, request, context, **kwargs):
        serializer = ZipBladeShapeSerializer()
        response = HttpResponse(content_type='application/zip')
        serializer.serialize(queryset=self.get_queryset(), model=Blade,
                             stream=response, fields=self.columns)
        response['Content-length'] = str(len(response.content))
        return response
