import logging

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.gis.db.models.functions import Transform
from django.core.exceptions import PermissionDenied
from django.db.models import Sum, OuterRef, F
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.utils.html import escape
from django.views.generic import CreateView
from mapentity.views import (MapEntityCreate, MapEntityUpdate, MapEntityList, MapEntityDetail, MapEntityFilter,
                             MapEntityDelete, MapEntityFormat, MapEntityDocument)
from rest_framework import permissions as rest_permissions, viewsets

from geotrek.authent.decorators import same_structure_required
from geotrek.common.mixins.views import CompletenessMixin, CustomColumnsMixin
from geotrek.common.models import RecordSource, TargetPortal
from geotrek.common.views import DocumentPublic, DocumentBookletPublic, MarkupPublic, normalize_annotation_column_name
from geotrek.common.viewsets import GeotrekMapentityViewSet
from geotrek.trekking.models import Trek
from .filters import TouristicContentFilterSet, TouristicEventFilterSet
from .forms import TouristicContentForm, TouristicEventForm, TouristicEventOrganizerFormPopup
from .models import (TouristicContent, TouristicEvent, TouristicContentCategory, TouristicEventOrganizer,
                     InformationDesk, TouristicEventParticipantCategory, TouristicEventParticipantCount)
from .serializers import (TouristicContentSerializer, TouristicEventSerializer,
                          TrekInformationDeskGeojsonSerializer,
                          TouristicContentGeojsonSerializer, TouristicEventGeojsonSerializer)


logger = logging.getLogger(__name__)


class TouristicContentList(CustomColumnsMixin, MapEntityList):
    queryset = TouristicContent.objects.existing()
    mandatory_columns = ['id', 'name']
    default_extra_columns = ['category']
    searchable_columns = ['id', 'name']

    @property
    def categories_list(self):
        used = TouristicContent.objects.values_list('category__pk')
        return TouristicContentCategory.objects.filter(pk__in=used)


class TouristicContentFilter(MapEntityFilter):
    model = TouristicContent
    filterset_class = TouristicContentFilterSet


class TouristicContentFormatList(MapEntityFormat, TouristicContentList):
    filterset_class = TouristicContentFilterSet
    mandatory_columns = ['id']
    default_extra_columns = [
        'structure', 'eid', 'name', 'category', 'type1', 'type2', 'description_teaser',
        'description', 'themes', 'contact', 'email', 'website', 'practical_info', 'label_accessibility',
        'accessibility', 'review', 'published', 'publication_date', 'source', 'portal', 'date_insert', 'date_update',
        'cities', 'districts', 'areas', 'approved', 'uuid',
    ]


class TouristicContentDetail(CompletenessMixin, MapEntityDetail):
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


class TouristicContentViewSet(GeotrekMapentityViewSet):
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


class TouristicEventList(CustomColumnsMixin, MapEntityList):
    queryset = TouristicEvent.objects.existing()
    mandatory_columns = ['id', 'name']
    default_extra_columns = ['type', 'begin_date', 'end_date']
    searchable_columns = ['id', 'name']


class TouristicEventFilter(MapEntityFilter):
    model = TouristicEvent
    filterset_class = TouristicEventFilterSet


class TouristicEventFormatList(MapEntityFormat, TouristicEventList):
    filterset_class = TouristicEventFilterSet
    mandatory_columns = ['id']
    default_extra_columns = [
        'structure', 'eid', 'name', 'type', 'description_teaser', 'description', 'themes',
        'begin_date', 'end_date', 'duration', 'meeting_point', 'start_time', 'end_time',
        'contact', 'email', 'website', 'organizers', 'speaker', 'accessibility', 'bookable',
        'capacity', 'booking', 'target_audience', 'practical_info',
        'date_insert', 'date_update', 'source', 'portal',
        'review', 'published', 'publication_date',
        'cities', 'districts', 'areas', 'approved', 'uuid',
        'cancelled', 'cancellation_reason', 'place',
        'preparation_duration', 'intervention_duration', 'price'
    ]

    @classmethod
    def build_participants_column_name(cls, category_label):
        return normalize_annotation_column_name(f"{_('Participants')} {category_label}")

    @classmethod
    def get_mandatory_columns(cls):
        mandatory_columns = ['id']
        if settings.ENABLE_EVENTS_PARTICIPANTS_DETAILED_EXPORT:
            categories_names = list(TouristicEventParticipantCategory.objects.order_by('order').values_list('label', flat=True))
            # Create column names for each unique category
            categories_columns_names = list(map(cls.build_participants_column_name, categories_names))
            # Add these column names to export
            mandatory_columns = mandatory_columns + categories_columns_names + ['total_participants']
        else:
            mandatory_columns = mandatory_columns + ['total_participants']
        return mandatory_columns

    def get_queryset(self):
        """Returns all events joined with a new column for each participant count"""

        queryset = super().get_queryset().select_related('place', 'cancellation_reason').prefetch_related('participants')

        if settings.ENABLE_EVENTS_PARTICIPANTS_DETAILED_EXPORT:
            # Get all participants categories, as unique ids and names
            categories = TouristicEventParticipantCategory.objects.order_by('order').values_list('id', 'label')

            # Iter over unique categories
            for category_id, label in categories:

                # Create column name for current category
                column_name = self.build_participants_column_name(label)

                # Create subquery to retrieve category count (renamed because of ambiguity with 'count' method)
                subquery = (TouristicEventParticipantCount.objects.filter(
                    event=OuterRef('pk'),
                    category=category_id
                ).annotate(
                        category_count=F('count')
                ).values('category_count'))

                # Annotate queryset with this cost query
                params = {column_name: subquery}
                queryset = queryset.annotate(**params).annotate(total_participants=Sum('participants__count'))
        else:
            return queryset.annotate(total_participants=Sum('participants__count'))
        return queryset


class TouristicEventDetail(CompletenessMixin, MapEntityDetail):
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


class TouristicEventOrganizerCreatePopup(CreateView):
    model = TouristicEventOrganizer
    form_class = TouristicEventOrganizerFormPopup

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not request.user.has_perm("tourism.add_touristiceventorganizer"):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        self.object = form.save()
        return HttpResponse("""
            <script type="text/javascript">opener.dismissAddAnotherPopup(window, "%s", "%s");</script>
        """ % (escape(form.instance._get_pk_val()), escape(form.instance)))


class TouristicEventDocumentPublic(TouristicEventDocumentPublicMixin, DocumentPublic):
    pass


class TouristicEventDocumentBookletPublic(TouristicEventDocumentPublicMixin, DocumentBookletPublic):
    pass


class TouristicEventMarkupPublic(TouristicEventDocumentPublicMixin, MarkupPublic):
    pass


class TouristicEventViewSet(GeotrekMapentityViewSet):
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


class TrekInformationDeskViewSet(viewsets.ModelViewSet):
    model = InformationDesk
    serializer_class = TrekInformationDeskGeojsonSerializer
    permission_classes = [rest_permissions.DjangoModelPermissionsOrAnonReadOnly]

    def get_queryset(self):
        pk = self.kwargs['pk']
        trek = get_object_or_404(Trek.objects.existing(), pk=pk)
        return trek.information_desks.all().annotate(api_geom=Transform("geom", settings.API_SRID))
