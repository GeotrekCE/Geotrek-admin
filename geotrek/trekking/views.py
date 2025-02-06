from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.gis.db.models.functions import Transform
from django.db.models.query import Prefetch
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404
from django.utils import translation
from django.utils.decorators import method_decorator
from django.utils.html import escape
from django.views.generic import CreateView
from django.views.generic.detail import BaseDetailView
from mapentity.helpers import alphabet_enumeration
from mapentity.views import (MapEntityList, MapEntityFormat, MapEntityDetail, MapEntityMapImage, MapEntityFilter,
                             MapEntityDocument, MapEntityCreate, MapEntityUpdate, MapEntityDelete, LastModifiedMixin)
from rest_framework import permissions as rest_permissions, viewsets

from geotrek.authent.decorators import same_structure_required
from geotrek.common.forms import AttachmentAccessibilityForm
from geotrek.common.mixins.views import CompletenessMixin, CustomColumnsMixin
from geotrek.common.models import Attachment, HDViewPoint, RecordSource, TargetPortal, Label
from geotrek.common.permissions import PublicOrReadPermMixin
from geotrek.common.views import DocumentPublic, DocumentBookletPublic, MarkupPublic
from geotrek.common.viewsets import GeotrekMapentityViewSet
from geotrek.core.models import AltimetryMixin
from geotrek.core.views import CreateFromTopologyMixin
from geotrek.infrastructure.models import Infrastructure
from geotrek.infrastructure.serializers import InfrastructureAPIGeojsonSerializer
from geotrek.signage.models import Signage
from geotrek.signage.serializers import SignageAPIGeojsonSerializer
from geotrek.zoning.models import District, City, RestrictedArea

from .filters import TrekFilterSet, POIFilterSet, ServiceFilterSet
from .forms import TrekForm, POIForm, WebLinkCreateFormPopup, ServiceForm
from .models import Trek, POI, WebLink, Service
from .serializers import (TrekGPXSerializer, TrekSerializer, POISerializer, ServiceSerializer, TrekPOIAPIGeojsonSerializer,
                          TrekServiceAPIGeojsonSerializer,
                          TrekGeojsonSerializer, POIGeojsonSerializer, ServiceGeojsonSerializer)


class FlattenPicturesMixin:
    def get_queryset(self):
        """ Override queryset to avoid attachment lookup while serializing.
        It will fetch attachments, and force ``pictures`` attribute of instances.
        """
        qs = super().get_queryset()
        qs.prefetch_related(Prefetch('attachments',
                                     queryset=Attachment.objects.filter(
                                         is_image=True
                                     ).exclude(title='mapimage').order_by('-starred', 'attachment_file'),
                                     to_attr="_pictures"))
        return qs


class TrekList(CustomColumnsMixin, FlattenPicturesMixin, MapEntityList):
    queryset = Trek.objects.existing()
    mandatory_columns = ['id', 'name']
    default_extra_columns = ['duration', 'difficulty', 'departure', 'thumbnail']
    unorderable_columns = ['thumbnail']
    searchable_columns = ['id', 'name', 'departure', 'arrival']


class TrekFilter(MapEntityFilter):
    model = Trek
    filterset_class = TrekFilterSet


class TrekFormatList(MapEntityFormat, TrekList):
    filterset_class = TrekFilterSet
    mandatory_columns = ['id', 'name']
    default_extra_columns = [
        'eid', 'eid2', 'structure', 'departure', 'arrival', 'duration', 'duration_pretty', 'description',
        'description_teaser', 'networks', 'advice', 'gear', 'ambiance', 'difficulty', 'information_desks',
        'themes', 'practice', 'ratings', 'ratings_description', 'accessibilities', 'accessibility_advice',
        'accessibility_covering', 'accessibility_exposure', 'accessibility_level', 'accessibility_signage',
        'accessibility_slope', 'accessibility_width', 'accessibility_infrastructure', 'access', 'route',
        'public_transport', 'advised_parking', 'web_links', 'labels', 'parking_location', 'points_reference',
        'children', 'parents', 'pois', 'review', 'published', 'publication_date', 'date_insert',
        'date_update', 'cities', 'districts', 'areas', 'source', 'portal', 'length_2d', 'uuid',
    ] + AltimetryMixin.COLUMNS


class TrekGPXDetail(LastModifiedMixin, PublicOrReadPermMixin, BaseDetailView):
    queryset = Trek.objects.existing()

    def render_to_response(self, context):
        gpx_serializer = TrekGPXSerializer()
        response = HttpResponse(content_type='application/gpx+xml')
        response['Content-Disposition'] = 'attachment; filename=%s.gpx' % self.get_object().slug
        gpx_serializer.serialize([self.get_object()], stream=response, gpx_field='geom_3d')
        return response


class TrekKMLDetail(LastModifiedMixin, PublicOrReadPermMixin, BaseDetailView):
    queryset = Trek.objects.existing()

    def render_to_response(self, context):
        trek = self.get_object()
        response = HttpResponse(trek.kml(),
                                content_type='application/vnd.google-earth.kml+xml')
        return response


class TrekDetail(CompletenessMixin, MapEntityDetail):
    queryset = Trek.objects.existing().select_related('topo_object', 'structure').prefetch_related(
        Prefetch('view_points',
                 queryset=HDViewPoint.objects.select_related('content_type', 'license'))
    )

    @property
    def icon_sizes(self):
        return {
            'POI': settings.TREK_ICON_SIZE_POI,
            'service': settings.TREK_ICON_SIZE_SERVICE,
            'signage': settings.TREK_ICON_SIZE_SIGNAGE,
            'infrastructure': settings.TREK_ICON_SIZE_INFRASTRUCTURE,
            'parking': settings.TREK_ICON_SIZE_PARKING,
            'information_desk': settings.TREK_ICON_SIZE_INFORMATION_DESK
        }

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['can_edit'] = self.get_object().same_structure(self.request.user)
        context['labels'] = Label.objects.all()
        context['accessibility_form'] = AttachmentAccessibilityForm(request=self.request, object=self.get_object())
        return context


class TrekMapImage(MapEntityMapImage):
    queryset = Trek.objects.existing()


class TrekDocument(MapEntityDocument):
    queryset = Trek.objects.existing()


class TrekDocumentPublicMixin:
    queryset = Trek.objects.existing()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        trek = self.get_object()

        context['headerimage_ratio'] = settings.EXPORT_HEADER_IMAGE_SIZE['trek']

        information_desks = list(trek.information_desks.all())
        if settings.TREK_EXPORT_INFORMATION_DESK_LIST_LIMIT > 0:
            information_desks = information_desks[:settings.TREK_EXPORT_INFORMATION_DESK_LIST_LIMIT]

        context['information_desks'] = information_desks
        pois = list(trek.published_pois.all())
        if settings.TREK_EXPORT_POI_LIST_LIMIT > 0:
            pois = pois[:settings.TREK_EXPORT_POI_LIST_LIMIT]
        letters = alphabet_enumeration(len(pois))
        for i, poi in enumerate(pois):
            poi.letter = letters[i]
        context['pois'] = pois
        infrastructures = list(trek.published_infrastructures.all())
        signages = list(trek.published_signages.all())
        context['infrastructures'] = infrastructures
        context['signages'] = signages
        context['object'] = context['trek'] = trek
        source = self.request.GET.get('source')
        if source:
            try:
                context['source'] = RecordSource.objects.get(name=source)
            except RecordSource.DoesNotExist:
                pass
        portal = self.request.GET.get('portal')
        if portal:
            try:
                context['portal'] = TargetPortal.objects.get(name=portal)
            except TargetPortal.DoesNotExist:
                pass
        return context

    def render_to_response(self, context, **response_kwargs):
        # Prepare altimetric graph
        trek = self.get_object()
        language = self.request.LANGUAGE_CODE
        trek.prepare_elevation_chart(language)
        return super().render_to_response(context, **response_kwargs)


class TrekDocumentPublic(TrekDocumentPublicMixin, DocumentPublic):
    pass


class TrekDocumentBookletPublic(TrekDocumentPublicMixin, DocumentBookletPublic):
    pass


class TrekMarkupPublic(TrekDocumentPublicMixin, MarkupPublic):
    pass


class TrekCreate(CreateFromTopologyMixin, MapEntityCreate):
    model = Trek
    form_class = TrekForm


class TrekUpdate(MapEntityUpdate):
    queryset = Trek.objects.existing()
    form_class = TrekForm

    @same_structure_required('trekking:trek_detail')
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class TrekDelete(MapEntityDelete):
    model = Trek

    @same_structure_required('trekking:trek_detail')
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class TrekViewSet(GeotrekMapentityViewSet):
    model = Trek
    serializer_class = TrekSerializer
    geojson_serializer_class = TrekGeojsonSerializer
    filterset_class = TrekFilterSet
    mapentity_list_class = TrekList

    def get_queryset(self):
        qs = self.model.objects.existing()
        if self.format_kwarg == 'geojson':
            qs = qs.annotate(api_geom=Transform('geom', settings.API_SRID))
            qs = qs.only('id', 'name', 'published')
        else:
            qs = qs.prefetch_related('attachments')
        return qs


class POIList(CustomColumnsMixin, FlattenPicturesMixin, MapEntityList):
    queryset = POI.objects.existing()
    mandatory_columns = ['id', 'name']
    default_extra_columns = ['type', 'thumbnail']
    unorderable_columns = ['thumbnail']
    searchable_columns = ['id', 'name', ]


class POIFilter(MapEntityFilter):
    model = POI
    filterset_class = POIFilterSet


class POIFormatList(MapEntityFormat, POIList):
    filterset_class = POIFilterSet
    mandatory_columns = ['id']
    default_extra_columns = [
        'structure', 'eid', 'name', 'type', 'description', 'treks',
        'review', 'published', 'publication_date',
        'structure', 'date_insert', 'date_update',
        'cities', 'districts', 'areas', 'uuid',
    ] + AltimetryMixin.COLUMNS

    def get_queryset(self):
        qs = super().get_queryset()

        denormalized = {}

        # Since Land layers should have less records, start by them.
        land_layers = [('districts', District),
                       ('cities', City),
                       ('areas', RestrictedArea)]
        for attrname, land_layer in land_layers:
            denormalized[attrname] = {}
            for d in land_layer.objects.all():
                overlapping = POI.objects.existing().filter(geom__within=d.geom)
                for pid in overlapping.values_list('id', flat=True):
                    denormalized[attrname].setdefault(pid, []).append(str(d))

        # Same for treks
        denormalized['treks'] = {}
        for d in Trek.objects.existing():
            for pid in d.pois.all():
                denormalized['treks'].setdefault(pid, []).append(d)
        for poi in qs:
            # Put denormalized in specific attribute used in serializers
            for attrname in denormalized.keys():
                overlapping = denormalized[attrname].get(poi.id, [])
                setattr(poi, '%s_csv_display' % attrname, ', '.join(overlapping))
            yield poi


class POIDetail(CompletenessMixin, MapEntityDetail):
    queryset = POI.objects.existing().prefetch_related(
        Prefetch('view_points',
                 queryset=HDViewPoint.objects.select_related('content_type', 'license'))
    ).select_related('type')

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['can_edit'] = self.get_object().same_structure(self.request.user)
        return context


class POIDocument(MapEntityDocument):
    model = POI


class POICreate(MapEntityCreate):
    model = POI
    form_class = POIForm


class POIUpdate(MapEntityUpdate):
    queryset = POI.objects.existing()
    form_class = POIForm

    @same_structure_required('trekking:poi_detail')
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class POIDelete(MapEntityDelete):
    model = POI

    @same_structure_required('trekking:poi_detail')
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class WebLinkCreatePopup(CreateView):
    model = WebLink
    form_class = WebLinkCreateFormPopup

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def form_valid(self, form):
        self.object = form.save()
        return HttpResponse("""
            <script type="text/javascript">opener.dismissAddAnotherPopup(window, "%s", "%s");</script>
        """ % (escape(form.instance._get_pk_val()), escape(form.instance)))


class POIViewSet(GeotrekMapentityViewSet):
    model = POI
    serializer_class = POISerializer
    geojson_serializer_class = POIGeojsonSerializer
    filterset_class = POIFilterSet
    mapentity_list_class = POIList

    def get_queryset(self):
        qs = self.model.objects.existing()
        if self.format_kwarg == 'geojson':
            qs = qs.annotate(api_geom=Transform('geom', settings.API_SRID))
            qs = qs.only('id', 'name', 'published')
        else:
            qs = qs.select_related('type', 'structure')
            qs = qs.prefetch_related('attachments')
        return qs


class TrekPOIViewSet(viewsets.ModelViewSet):
    model = POI
    serializer_class = TrekPOIAPIGeojsonSerializer
    permission_classes = [rest_permissions.DjangoModelPermissionsOrAnonReadOnly]

    def get_queryset(self):
        pk = self.kwargs['pk']
        trek = get_object_or_404(Trek.objects.existing(), pk=pk)
        if not self.request.user.has_perm('trekking.read_poi') and not trek.is_public():
            raise Http404
        return trek.pois.filter(published=True).annotate(api_geom=Transform("geom", settings.API_SRID)).select_related('type',)


class TrekSignageViewSet(viewsets.ModelViewSet):
    model = Signage
    serializer_class = SignageAPIGeojsonSerializer
    permission_classes = [rest_permissions.DjangoModelPermissionsOrAnonReadOnly]

    def get_queryset(self):
        pk = self.kwargs['pk']
        trek = get_object_or_404(Trek.objects.existing(), pk=pk)
        if not self.request.user.has_perm('trekking.read_signage') and not trek.is_public():
            raise Http404
        return trek.signages.filter(published=True).annotate(api_geom=Transform("geom", settings.API_SRID))


class TrekInfrastructureViewSet(viewsets.ModelViewSet):
    model = Infrastructure
    serializer_class = InfrastructureAPIGeojsonSerializer
    permission_classes = [rest_permissions.DjangoModelPermissionsOrAnonReadOnly]

    def get_queryset(self):
        pk = self.kwargs['pk']
        trek = get_object_or_404(Trek.objects.existing(), pk=pk)
        if not self.request.user.has_perm('infrastructure.read_infrastructure') and not trek.is_public():
            raise Http404
        return trek.infrastructures.filter(published=True).annotate(api_geom=Transform("geom", settings.API_SRID))


class ServiceList(CustomColumnsMixin, MapEntityList):
    queryset = Service.objects.existing()
    mandatory_columns = ['id', 'name']
    default_extra_columns = []
    searchable_columns = ['id']


class ServiceFilter(MapEntityFilter):
    model = Service
    filterset_class = ServiceFilterSet


class ServiceFormatList(MapEntityFormat, ServiceList):
    filterset_class = ServiceFilterSet
    mandatory_columns = ['id']
    default_extra_columns = [
        'id', 'eid', 'type', 'uuid',
    ] + AltimetryMixin.COLUMNS


class ServiceDetail(MapEntityDetail):
    queryset = Service.objects.existing()

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['can_edit'] = self.get_object().same_structure(self.request.user)
        return context


class ServiceCreate(MapEntityCreate):
    model = Service
    form_class = ServiceForm


class ServiceUpdate(MapEntityUpdate):
    queryset = Service.objects.existing()
    form_class = ServiceForm

    @same_structure_required('trekking:service_detail')
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class ServiceDelete(MapEntityDelete):
    model = Service

    @same_structure_required('trekking:service_detail')
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class ServiceViewSet(GeotrekMapentityViewSet):
    model = Service
    serializer_class = ServiceSerializer
    geojson_serializer_class = ServiceGeojsonSerializer
    filterset_class = ServiceFilterSet
    mapentity_list_class = ServiceList

    def get_queryset(self):
        qs = self.model.objects.existing().select_related('type')
        if self.format_kwarg == 'geojson':
            qs = qs.annotate(api_geom=Transform('geom', settings.API_SRID))
            qs = qs.only('id', 'type')
        return qs


class TrekServiceViewSet(viewsets.ModelViewSet):
    model = Service
    serializer_class = TrekServiceAPIGeojsonSerializer
    permission_classes = [rest_permissions.DjangoModelPermissionsOrAnonReadOnly]

    def get_queryset(self):
        pk = self.kwargs['pk']
        trek = get_object_or_404(Trek.objects.existing(), pk=pk)
        if not self.request.user.has_perm('trekking.read_service') and not trek.is_public():
            raise Http404
        return trek.services.filter(type__published=True).annotate(api_geom=Transform("geom", settings.API_SRID))


# Translations for public PDF
translation.gettext_noop("Advices")
translation.gettext_noop("Gear")
translation.gettext_noop("All useful information")
translation.gettext_noop("Altimetric profile")
translation.gettext_noop("Attribution")
translation.gettext_noop("Geographical location")
translation.gettext_noop("Markings")
translation.gettext_noop("Max elevation")
translation.gettext_noop("Min elevation")
translation.gettext_noop("On your path...")
translation.gettext_noop("Powered by geotrek.fr")
translation.gettext_noop("The national park is an unrestricted natural area but subjected to regulations which must be known by all visitors.")
translation.gettext_noop("This hike is in the core of the national park")
translation.gettext_noop("Trek ascent")
translation.gettext_noop("Useful information")
