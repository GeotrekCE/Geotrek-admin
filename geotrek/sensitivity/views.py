import json
import logging

from django.conf import settings
from django.contrib.gis.db.models.functions import Transform
from django.db.models import F, Case, When
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404
from django.views.generic.detail import BaseDetailView
from mapentity.views import (MapEntityCreate, MapEntityUpdate, MapEntityList, MapEntityDetail,
                             MapEntityDelete, MapEntityFormat, LastModifiedMixin)
from rest_framework import permissions as rest_permissions, viewsets

from geotrek.authent.decorators import same_structure_required
from geotrek.common.functions import GeometryType, Buffer, Area
from geotrek.common.mixins.api import APIViewSet
from geotrek.common.mixins.views import CustomColumnsMixin, DuplicateMixin, DuplicateDetailMixin
from geotrek.common.permissions import PublicOrReadPermMixin
from geotrek.common.viewsets import GeotrekMapentityViewSet
from .filters import SensitiveAreaFilterSet
from .forms import SensitiveAreaForm, RegulatorySensitiveAreaForm
from .models import SensitiveArea, Species
from .serializers import SensitiveAreaSerializer, SensitiveAreaAPIGeojsonSerializer, SensitiveAreaAPISerializer, \
    SensitiveAreaGeojsonSerializer

if 'geotrek.trekking' in settings.INSTALLED_APPS:
    from geotrek.trekking.models import Trek

if 'geotrek.diving' in settings.INSTALLED_APPS:
    from geotrek.diving.models import Dive

logger = logging.getLogger(__name__)


class SensitiveAreaList(CustomColumnsMixin, MapEntityList):
    queryset = SensitiveArea.objects.existing()
    filterform = SensitiveAreaFilterSet
    mandatory_columns = ['id', 'checkbox', 'species']
    default_extra_columns = ['category']
    unorderable_columns = ['checkbox']


class SensitiveAreaFormatList(MapEntityFormat, SensitiveAreaList):
    mandatory_columns = ['id']
    default_extra_columns = [
        'species', 'published', 'description', 'contact', 'radius', 'pretty_period', 'pretty_practices',
    ]


class SensitiveAreaDetail(DuplicateDetailMixin, MapEntityDetail):
    queryset = SensitiveArea.objects.existing()

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['can_edit'] = self.object.same_structure(self.request.user)
        return context


class SensitiveAreaRadiiMixin:
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        species = Species.objects.filter(category=Species.SPECIES)
        context['radii'] = json.dumps({
            str(s.id): settings.SENSITIVITY_DEFAULT_RADIUS if s.radius is None else s.radius for s in species
        })
        return context


class SensitiveAreaCreate(SensitiveAreaRadiiMixin, MapEntityCreate):
    model = SensitiveArea

    def get_form_class(self):
        if self.request.GET.get('category') == str(Species.REGULATORY):
            return RegulatorySensitiveAreaForm
        return SensitiveAreaForm


class SensitiveAreaUpdate(SensitiveAreaRadiiMixin, MapEntityUpdate):
    queryset = SensitiveArea.objects.existing()

    def get_form_class(self):
        if self.object.species.category == Species.REGULATORY:
            return RegulatorySensitiveAreaForm
        return SensitiveAreaForm

    @same_structure_required('sensitivity:sensitivearea_detail')
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class SensitiveAreaDelete(MapEntityDelete):
    model = SensitiveArea

    @same_structure_required('sensitivity:sensitivearea_detail')
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class SensitiveAreaViewSet(DuplicateMixin, GeotrekMapentityViewSet):
    model = SensitiveArea
    serializer_class = SensitiveAreaSerializer
    geojson_serializer_class = SensitiveAreaGeojsonSerializer
    filterset_class = SensitiveAreaFilterSet
    mapentity_list_class = SensitiveAreaList

    def get_queryset(self):
        qs = self.model.objects.existing().select_related('species')
        if self.format_kwarg == 'geojson':
            qs = qs.annotate(api_geom=Transform('geom', settings.API_SRID))
            qs = qs.only('id', 'species')
        return qs


class SensitiveAreaAPIViewSet(APIViewSet):
    model = SensitiveArea
    serializer_class = SensitiveAreaAPISerializer
    geojson_serializer_class = SensitiveAreaAPIGeojsonSerializer

    def get_queryset(self):
        qs = SensitiveArea.objects.existing()
        qs = qs.filter(published=True)
        qs = qs.prefetch_related('species')
        qs = qs.annotate(geom_type=GeometryType(F('geom')))
        qs = qs.annotate(geom2d_transformed=Case(
            When(geom_type='POINT', then=Transform(Buffer(F('geom'), F('species__radius'), 4), settings.API_SRID)),
            When(geom_type__in=('POLYGON', 'MULTIPOLYGON'), then=Transform(F('geom'), settings.API_SRID))
        ))
        # Ensure smaller areas are at the end of the list, ie above bigger areas on the map
        # to ensure we can select every area in case of overlapping
        qs = qs.annotate(area=Area('geom2d_transformed')).order_by('-area')

        if 'practices' in self.request.GET:
            qs = qs.filter(species__practices__name__in=self.request.GET['practices'].split(','))

        return qs


if 'geotrek.trekking' in settings.INSTALLED_APPS:
    class TrekSensitiveAreaViewSet(viewsets.ModelViewSet):
        model = SensitiveArea
        serializer_class = SensitiveAreaAPIGeojsonSerializer
        permission_classes = [rest_permissions.DjangoModelPermissionsOrAnonReadOnly]

        def get_queryset(self):
            pk = self.kwargs['pk']
            trek = get_object_or_404(Trek.objects.existing(), pk=pk)
            if not trek.is_public():
                raise Http404
            qs = trek.published_sensitive_areas
            qs = qs.prefetch_related('species')
            qs = qs.annotate(geom_type=GeometryType(F('geom')))
            qs = qs.annotate(geom2d_transformed=Case(
                When(geom_type='POINT', then=Transform(Buffer(F('geom'), F('species__radius'), 4), settings.API_SRID)),
                When(geom_type='POLYGON', then=Transform(F('geom'), settings.API_SRID))
            ))
            # Ensure smaller areas are at the end of the list, ie above bigger areas on the map
            # to ensure we can select every area in case of overlapping
            qs = qs.annotate(area=Area('geom2d_transformed')).order_by('-area')

            if 'practices' in self.request.GET:
                qs = qs.filter(species__practices__name__in=self.request.GET['practices'].split(','))

            return qs

if 'geotrek.diving' in settings.INSTALLED_APPS:
    class DiveSensitiveAreaViewSet(viewsets.ModelViewSet):
        model = SensitiveArea
        serializer_class = SensitiveAreaAPIGeojsonSerializer
        permission_classes = [rest_permissions.DjangoModelPermissionsOrAnonReadOnly]

        def get_queryset(self):
            pk = self.kwargs['pk']
            dive = get_object_or_404(Dive.objects.existing(), pk=pk)
            if not dive.is_public:
                raise Http404
            qs = dive.published_sensitive_areas
            qs = qs.prefetch_related('species')
            qs = qs.annotate(geom_type=GeometryType(F('geom')))
            qs = qs.annotate(geom2d_transformed=Case(
                When(geom_type='POINT', then=Transform(Buffer(F('geom'), F('species__radius'), 4), settings.API_SRID)),
                When(geom_type='POLYGON', then=Transform(F('geom'), settings.API_SRID))
            ))
            # Ensure smaller areas are at the end of the list, ie above bigger areas on the map
            # to ensure we can select every area in case of overlapping
            qs = qs.annotate(area=Area('geom2d_transformed')).order_by('-area')

            if 'practices' in self.request.GET:
                qs = qs.filter(species__practices__name__in=self.request.GET['practices'].split(','))

            return qs


class SensitiveAreaKMLDetail(LastModifiedMixin, PublicOrReadPermMixin, BaseDetailView):
    queryset = SensitiveArea.objects.existing()

    def render_to_response(self, context):
        area = self.get_object()
        response = HttpResponse(area.kml(),
                                content_type='application/vnd.google-earth.kml+xml')
        return response
