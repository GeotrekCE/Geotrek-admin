import logging

from django.conf import settings
from django.contrib.gis.db.models.functions import Transform
from django.http import HttpResponse
from django.utils import translation
from django.utils.functional import classproperty
from mapentity.views import (MapEntityList, MapEntityFormat, MapEntityDetail,
                             MapEntityDocument, MapEntityCreate, MapEntityUpdate, MapEntityDelete)

from geotrek.authent.decorators import same_structure_required
from geotrek.common.mixins.api import APIViewSet
from geotrek.common.mixins.forms import FormsetMixin
from geotrek.common.mixins.views import CustomColumnsMixin
from geotrek.common.viewsets import GeotrekMapentityViewSet
from geotrek.core.models import AltimetryMixin
from .filters import SignageFilterSet, BladeFilterSet
from .forms import SignageForm, BladeForm, LineFormset
from .models import Signage, Blade
from .serializers import (SignageSerializer, BladeSerializer,
                          SignageAPIGeojsonSerializer, CSVBladeSerializer, ZipBladeShapeSerializer,
                          SignageAPISerializer, BladeAPISerializer, BladeAPIGeojsonSerializer, SignageGeojsonSerializer,
                          BladeGeojsonSerializer)

logger = logging.getLogger(__name__)


class LineMixin(FormsetMixin):
    context_name = 'line_formset'
    formset_class = LineFormset


class SignageList(CustomColumnsMixin, MapEntityList):
    queryset = Signage.objects.existing()
    filterform = SignageFilterSet
    mandatory_columns = ['id', 'name']
    default_extra_columns = ['code', 'type', 'condition']
    searchable_columns = ['id', 'name', 'code']


class SignageFormatList(MapEntityFormat, SignageList):
    mandatory_columns = ['id']
    default_extra_columns = [
        'structure', 'name', 'code', 'type', 'condition', 'description',
        'implantation_year', 'published', 'date_insert',
        'date_update', 'cities', 'districts', 'areas', 'lat_value', 'lng_value',
        'printed_elevation', 'sealing', 'access', 'manager', 'uuid',
    ] + AltimetryMixin.COLUMNS


class SignageDetail(MapEntityDetail):
    queryset = Signage.objects.existing()

    def dispatch(self, *args, **kwargs):
        lang = self.request.GET.get('lang')
        if lang:
            translation.activate(lang)
            self.request.LANGUAGE_CODE = lang
        return super().dispatch(*args, **kwargs)

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
    geojson_serializer_class = SignageGeojsonSerializer
    filterset_class = SignageFilterSet
    mapentity_list_class = SignageList

    def get_queryset(self):
        qs = self.model.objects.existing()
        if self.format_kwarg == 'geojson':
            qs = qs.annotate(api_geom=Transform('geom', settings.API_SRID))
            qs = qs.only('id', 'name', 'published')
        else:
            qs = qs.select_related('structure', 'manager', 'sealing', 'access', 'type', 'condition')
        return qs


class SignageAPIViewSet(APIViewSet):
    model = Signage
    serializer_class = SignageAPISerializer
    geojson_serializer_class = SignageAPIGeojsonSerializer

    def get_queryset(self):
        return Signage.objects.existing().filter(published=True).annotate(api_geom=Transform("geom", settings.API_SRID))


class BladeDetail(MapEntityDetail):
    queryset = Blade.objects.existing()

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
    queryset = Blade.objects.existing()
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


class BladeList(CustomColumnsMixin, MapEntityList):
    queryset = Blade.objects.existing()
    filterform = BladeFilterSet
    mandatory_columns = ['id', 'number']
    default_extra_columns = ['type', 'color', 'direction']
    searchable_columns = ['id', 'number']

    @classproperty
    def columns(cls):
        columns = super().columns
        if not settings.DIRECTION_ON_LINES_ENABLED:
            return columns
        columns.remove('direction')
        if 'direction' in cls.get_custom_columns():
            logger.warning(
                f"Ignoring entry 'direction' in COLUMNS_LISTS for view {cls.__name__} because the setting "
                "DIRECTION_ON_LINES is enabled."
            )
        return columns


class BladeFormatList(MapEntityFormat, BladeList):
    mandatory_columns = ['id']
    default_extra_columns = ['city', 'signage', 'printedelevation', 'bladecode', 'type', 'color', 'direction',
                             'condition', 'coordinates']
    columns_line = ['number', 'direction', 'text', 'distance_pretty', 'time_pretty', 'pictograms']

    def csv_view(self, request, context, **kwargs):
        serializer = CSVBladeSerializer()
        response = HttpResponse(content_type='text/csv')
        columns_line = self._adapt_direction_on_lines_visibility(self.columns_line)
        serializer.serialize(queryset=self.get_queryset(), stream=response,
                             model=self.get_model(), fields=self.columns, line_fields=columns_line,
                             ensure_ascii=True)
        return response

    def shape_view(self, request, context, **kwargs):
        serializer = ZipBladeShapeSerializer()
        response = HttpResponse(content_type='application/zip')
        serializer.serialize(queryset=self.get_queryset(), model=Blade,
                             stream=response, fields=self.columns)
        response['Content-length'] = str(len(response.content))
        return response

    @staticmethod
    def _adapt_direction_on_lines_visibility(columns):
        columns = columns.copy()
        if not settings.DIRECTION_ON_LINES_ENABLED and 'direction' in columns:
            columns.remove('direction')
        return columns


class BladeViewSet(GeotrekMapentityViewSet):
    model = Blade
    serializer_class = BladeSerializer
    geojson_serializer_class = BladeGeojsonSerializer
    filterset_class = BladeFilterSet
    mapentity_list_class = BladeList

    def get_queryset(self):
        qs = self.model.objects.existing()
        if self.format_kwarg == 'geojson':
            qs = qs.only('id', 'number')
        return qs


class BladeAPIViewSet(APIViewSet):
    model = Blade
    serializer_class = BladeAPISerializer
    geojson_serializer_class = BladeAPIGeojsonSerializer

    def get_queryset(self):
        return Blade.objects.existing().annotate(api_geom=Transform("signage__geom", settings.API_SRID))
