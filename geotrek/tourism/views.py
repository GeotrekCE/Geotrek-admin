import logging
import os

from django.conf import settings
from django.contrib.gis.db.models.functions import Transform
from django.db.models import Q, Sum
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext as _
from django.views.generic import DetailView
from django_filters.rest_framework import DjangoFilterBackend
from mapentity.views import (MapEntityCreate, MapEntityUpdate, MapEntityList, MapEntityDetail,
                             MapEntityDelete, MapEntityFormat, MapEntityDocument)
from rest_framework import permissions as rest_permissions, viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from geotrek.authent.decorators import same_structure_required
from geotrek.common.mixins.api import APIViewSet
from geotrek.common.mixins.views import (CompletenessMixin, CustomColumnsMixin, MetaMixin,
                                         DuplicateMixin, DuplicateDetailMixin)
from geotrek.common.models import RecordSource, TargetPortal
from geotrek.common.views import DocumentPublic, DocumentBookletPublic, MarkupPublic
from geotrek.common.viewsets import GeotrekMapentityViewSet
from geotrek.trekking.models import Trek
from .filters import TouristicContentFilterSet, TouristicEventFilterSet, TouristicEventApiFilterSet
from .forms import TouristicContentForm, TouristicEventForm
from .models import (TouristicContent, TouristicEvent, TouristicContentCategory, InformationDesk)
from .serializers import (TouristicContentSerializer, TouristicEventSerializer,
                          TouristicContentAPIGeojsonSerializer, TouristicEventAPIGeojsonSerializer,
                          InformationDeskGeojsonSerializer, TouristicContentAPISerializer, TouristicEventAPISerializer,
                          TouristicContentGeojsonSerializer, TouristicEventGeojsonSerializer)

if 'geotrek.diving' in settings.INSTALLED_APPS:
    from geotrek.diving.models import Dive


logger = logging.getLogger(__name__)


class TouristicContentList(CustomColumnsMixin, MapEntityList):
    queryset = TouristicContent.objects.existing()
    filterform = TouristicContentFilterSet
    mandatory_columns = ['id', 'name']
    default_extra_columns = ['category']
    searchable_columns = ['id', 'name']

    @property
    def categories_list(self):
        used = TouristicContent.objects.values_list('category__pk')
        return TouristicContentCategory.objects.filter(pk__in=used)


class TouristicContentFormatList(MapEntityFormat, TouristicContentList):
    mandatory_columns = ['id']
    default_extra_columns = [
        'structure', 'eid', 'name', 'category', 'type1', 'type2', 'description_teaser',
        'description', 'themes', 'contact', 'email', 'website', 'practical_info', 'label_accessibility',
        'accessibility', 'review', 'published', 'publication_date', 'source', 'portal', 'date_insert', 'date_update',
        'cities', 'districts', 'areas', 'approved', 'uuid',
    ]


class TouristicContentDetail(DuplicateDetailMixin, CompletenessMixin, MapEntityDetail):
    queryset = TouristicContent.objects.existing()

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['can_edit'] = self.get_object().same_structure(self.request.user)
        return context


class TouristicContentCreate(MapEntityCreate):
    model = TouristicContent
    form_class = TouristicContentForm

    def get_initial(self):
        """
        Returns the initial data to use for forms on this view.
        """
        initial = super().get_initial()
        try:
            category = int(self.request.GET.get('category'))
            initial['category'] = category
        except (TypeError, ValueError):
            pass
        return initial


class TouristicContentUpdate(MapEntityUpdate):
    queryset = TouristicContent.objects.existing()
    form_class = TouristicContentForm

    @same_structure_required('tourism:touristiccontent_detail')
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class TouristicContentDelete(MapEntityDelete):
    model = TouristicContent

    @same_structure_required('tourism:touristiccontent_detail')
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class TouristicContentDocument(MapEntityDocument):
    queryset = TouristicContent.objects.existing()


class TouristicContentDocumentPublicMixin:
    queryset = TouristicContent.objects.existing()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        content = self.get_object()

        context['headerimage_ratio'] = settings.EXPORT_HEADER_IMAGE_SIZE['touristiccontent']

        context['object'] = context['content'] = content
        source = self.request.GET.get('source')
        if source:
            try:
                context['source'] = RecordSource.objects.get(name=source)
            except RecordSource.DoesNotExist:
                pass
        portal = self.request.GET.get('portal', None)

        if portal:
            try:
                context['portal'] = TargetPortal.objects.get(name=portal)
            except TargetPortal.DoesNotExist:
                pass

        return context


class TouristicContentDocumentPublic(TouristicContentDocumentPublicMixin, DocumentPublic):
    pass


class TouristicContentDocumentBookletPublic(TouristicContentDocumentPublicMixin, DocumentBookletPublic):
    pass


class TouristicContentMarkupPublic(TouristicContentDocumentPublicMixin, MarkupPublic):
    pass


class TouristicContentMeta(MetaMixin, DetailView):
    model = TouristicContent
    template_name = 'tourism/touristiccontent_meta.html'


class TouristicContentViewSet(DuplicateMixin, GeotrekMapentityViewSet):
    model = TouristicContent
    serializer_class = TouristicContentSerializer
    geojson_serializer_class = TouristicContentGeojsonSerializer
    filterset_class = TouristicContentFilterSet
    mapentity_list_class = TouristicContentList

    def get_queryset(self):
        qs = self.model.objects.existing()
        if self.format_kwarg == 'geojson':
            qs = qs.annotate(api_geom=Transform('geom', settings.API_SRID))
            qs = qs.only('id', 'name')
        return qs


class TouristicContentAPIViewSet(APIViewSet):
    model = TouristicContent
    serializer_class = TouristicContentAPISerializer
    geojson_serializer_class = TouristicContentAPIGeojsonSerializer

    def get_queryset(self):
        qs = TouristicContent.objects.existing()
        qs = qs.filter(published=True)

        if 'source' in self.request.GET:
            qs = qs.filter(source__name__in=self.request.GET['source'].split(','))

        if 'portal' in self.request.GET:
            qs = qs.filter(Q(portal__name=self.request.GET['portal']) | Q(portal=None))

        qs = qs.annotate(api_geom=Transform("geom", settings.API_SRID))
        return qs


class TouristicEventList(CustomColumnsMixin, MapEntityList):
    queryset = TouristicEvent.objects.existing()
    filterform = TouristicEventFilterSet
    mandatory_columns = ['id', 'name']
    default_extra_columns = ['type', 'begin_date', 'end_date']
    searchable_columns = ['id', 'name']


class TouristicEventFormatList(MapEntityFormat, TouristicEventList):
    mandatory_columns = ['id']
    default_extra_columns = [
        'structure', 'eid', 'name', 'type', 'description_teaser', 'description', 'themes',
        'begin_date', 'end_date', 'duration', 'meeting_point', 'start_time', 'end_time',
        'contact', 'email', 'website', 'organizer', 'speaker', 'accessibility', 'bookable',
        'capacity', 'booking', 'target_audience', 'practical_info',
        'date_insert', 'date_update', 'source', 'portal',
        'review', 'published', 'publication_date',
        'cities', 'districts', 'areas', 'approved', 'uuid',
        'cancelled', 'cancellation_reason', 'total_participants', 'place',
        'preparation_duration', 'intervention_duration',
    ]

    def get_queryset(self):
        qs = super().get_queryset().select_related('place', 'cancellation_reason').prefetch_related('participants')
        return qs.annotate(total_participants=Sum('participants__count'))


class TouristicEventDetail(DuplicateDetailMixin, CompletenessMixin, MapEntityDetail):
    queryset = TouristicEvent.objects.existing().select_related('place', 'cancellation_reason').prefetch_related('participants')

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['can_edit'] = self.get_object().same_structure(self.request.user)
        return context


class TouristicEventCreate(MapEntityCreate):
    model = TouristicEvent
    form_class = TouristicEventForm


class TouristicEventUpdate(MapEntityUpdate):
    queryset = TouristicEvent.objects.existing()
    form_class = TouristicEventForm

    @same_structure_required('tourism:touristicevent_detail')
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class TouristicEventDelete(MapEntityDelete):
    model = TouristicEvent

    @same_structure_required('tourism:touristicevent_detail')
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class TouristicEventDocument(MapEntityDocument):
    queryset = TouristicEvent.objects.existing()


class TouristicEventDocumentPublicMixin:
    queryset = TouristicEvent.objects.existing()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event = self.get_object()

        context['headerimage_ratio'] = settings.EXPORT_HEADER_IMAGE_SIZE['touristicevent']
        context['object'] = context['event'] = event
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


class TouristicEventDocumentPublic(TouristicEventDocumentPublicMixin, DocumentPublic):
    pass


class TouristicEventDocumentBookletPublic(TouristicEventDocumentPublicMixin, DocumentBookletPublic):
    pass


class TouristicEventMarkupPublic(TouristicEventDocumentPublicMixin, MarkupPublic):
    pass


class TouristicEventMeta(MetaMixin, DetailView):
    model = TouristicEvent
    template_name = 'tourism/touristicevent_meta.html'


class TouristicEventViewSet(DuplicateMixin, GeotrekMapentityViewSet):
    model = TouristicEvent
    serializer_class = TouristicEventSerializer
    geojson_serializer_class = TouristicEventGeojsonSerializer
    filterset_class = TouristicEventFilterSet
    mapentity_list_class = TouristicEventList

    def get_queryset(self):
        qs = self.model.objects.existing()
        if self.format_kwarg == 'geojson':
            qs = qs.annotate(api_geom=Transform('geom', settings.API_SRID))
            qs = qs.only('id', 'name')
        else:
            qs = qs.select_related('place', 'cancellation_reason').prefetch_related('participants')
        return qs


class TouristicEventAPIViewSet(APIViewSet):
    model = TouristicEvent
    serializer_class = TouristicEventAPISerializer
    geojson_serializer_class = TouristicEventAPIGeojsonSerializer
    filter_backends = [DjangoFilterBackend, ]
    filterset_class = TouristicEventApiFilterSet

    def get_queryset(self):
        qs = TouristicEvent.objects.existing()
        qs = qs.filter(published=True)

        if 'source' in self.request.GET:
            qs = qs.filter(source__name__in=self.request.GET['source'].split(','))

        if 'portal' in self.request.GET:
            qs = qs.filter(Q(portal__name=self.request.GET['portal']) | Q(portal=None))

        qs = qs.annotate(api_geom=Transform("geom", settings.API_SRID))
        return qs


class InformationDeskViewSet(viewsets.ModelViewSet):
    model = InformationDesk
    queryset = InformationDesk.objects.all()
    serializer_class = InformationDeskGeojsonSerializer
    permission_classes = [rest_permissions.DjangoModelPermissionsOrAnonReadOnly]

    def get_queryset(self):
        qs = super().get_queryset()
        if self.kwargs.get('type'):
            qs = qs.filter(type_id=self.kwargs['type'])
        qs = qs.annotate(api_geom=Transform("geom", settings.API_SRID))
        return qs


class TrekInformationDeskViewSet(viewsets.ModelViewSet):
    model = InformationDesk
    serializer_class = InformationDeskGeojsonSerializer
    permission_classes = [rest_permissions.DjangoModelPermissionsOrAnonReadOnly]

    def get_queryset(self):
        pk = self.kwargs['pk']
        trek = get_object_or_404(Trek.objects.existing(), pk=pk)
        return trek.information_desks.all().annotate(api_geom=Transform("geom", settings.API_SRID))


class TrekTouristicContentViewSet(viewsets.ModelViewSet):
    model = TouristicContent
    serializer_class = TouristicContentAPIGeojsonSerializer
    permission_classes = [rest_permissions.DjangoModelPermissionsOrAnonReadOnly]

    def get_queryset(self):
        trek = get_object_or_404(Trek.objects.existing(), pk=self.kwargs['pk'])
        if not trek.is_public():
            raise Http404
        queryset = trek.touristic_contents.filter(published=True)

        if 'categories' in self.request.GET:
            queryset = queryset.filter(category__pk__in=self.request.GET['categories'].split(','))

        if 'source' in self.request.GET:
            queryset = queryset.filter(source__name__in=self.request.GET['source'].split(','))

        if 'portal' in self.request.GET:
            queryset = queryset.filter(portal__name=self.request.GET['portal'])

        return queryset.annotate(api_geom=Transform("geom", settings.API_SRID))


class TrekTouristicEventViewSet(viewsets.ModelViewSet):
    model = TouristicEvent
    serializer_class = TouristicEventAPIGeojsonSerializer
    permission_classes = [rest_permissions.DjangoModelPermissionsOrAnonReadOnly]

    def get_queryset(self):
        trek = get_object_or_404(Trek.objects.existing(), pk=self.kwargs['pk'])
        if not trek.is_public():
            raise Http404
        queryset = trek.touristic_events.filter(published=True)

        if 'source' in self.request.GET:
            queryset = queryset.filter(source__name__in=self.request.GET['source'].split(','))

        if 'portal' in self.request.GET:
            queryset = queryset.filter(portal__name=self.request.GET['portal'])

        return queryset.annotate(api_geom=Transform("geom", settings.API_SRID))


if 'geotrek.diving' in settings.INSTALLED_APPS:
    class DiveTouristicContentViewSet(viewsets.ModelViewSet):
        model = TouristicContent
        permission_classes = [rest_permissions.DjangoModelPermissionsOrAnonReadOnly]

        def get_serializer_class(self):
            renderer, media_type = self.perform_content_negotiation(self.request)
            if getattr(renderer, 'format') == 'geojson':
                return TouristicContentAPIGeojsonSerializer
            else:
                return TouristicContentAPISerializer

        def get_queryset(self):
            dive = get_object_or_404(Dive.objects.existing(), pk=self.kwargs['pk'])
            queryset = dive.touristic_contents.filter(published=True)

            if 'categories' in self.request.GET:
                queryset = queryset.filter(category__pk__in=self.request.GET['categories'].split(','))

            if 'source' in self.request.GET:
                queryset = queryset.filter(source__name__in=self.request.GET['source'].split(','))

            if 'portal' in self.request.GET:
                queryset = queryset.filter(portal__name=self.request.GET['portal'])

            return queryset.annotate(api_geom=Transform("geom", settings.API_SRID))

    class DiveTouristicEventViewSet(viewsets.ModelViewSet):
        model = TouristicEvent
        permission_classes = [rest_permissions.DjangoModelPermissionsOrAnonReadOnly]

        def get_serializer_class(self):
            renderer, media_type = self.perform_content_negotiation(self.request)
            if getattr(renderer, 'format') == 'geojson':
                return TouristicEventAPIGeojsonSerializer
            else:
                return TouristicEventAPISerializer

        def get_queryset(self):
            dive = get_object_or_404(Dive.objects.existing(), pk=self.kwargs['pk'])

            queryset = dive.touristic_events.filter(published=True)
            if 'source' in self.request.GET:
                queryset = queryset.filter(source__name__in=self.request.GET['source'].split(','))
            if 'portal' in self.request.GET:
                queryset = queryset.filter(portal__name=self.request.GET['portal'])
            return queryset.annotate(api_geom=Transform("geom", settings.API_SRID))


class TouristicCategoryView(APIView):
    """ touristiccategories.json generation for API """
    renderer_classes = (JSONRenderer,)
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, request, format=None, lang=None):
        response = []
        content_categories = TouristicContentCategory.objects.all()

        if request.GET.get('categories', False):
            categories = request.GET['categories'].split(',')
            content_categories.filter(pk__in=categories)

        for cont_cat in content_categories:
            response.append({'id': cont_cat.prefixed_id,
                             'label': cont_cat.label,
                             'type1_label': cont_cat.type1_label,
                             'type2_label': cont_cat.type2_label,
                             'pictogram': os.path.join(settings.MEDIA_URL, cont_cat.pictogram.url),
                             'order': cont_cat.order,
                             'slug': 'touristic-content'})

        if request.GET.get('events', False):
            response.append({'id': 'E',
                             'label': _("Touristic events"),
                             'type1_label': "",
                             'type2_label': "",
                             'pictogram': os.path.join(settings.STATIC_URL, 'tourism', 'touristicevent.svg'),
                             'order': None,
                             'slug': 'touristic-event'})

        return Response(response)
