import logging

import requests
from requests.exceptions import RequestException
import geojson
from djgeojson.views import GeoJSONLayerView
from django.conf import settings
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.decorators.cache import cache_page
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from mapentity.views import (JSONResponseMixin, MapEntityCreate,
                             MapEntityUpdate, MapEntityLayer, MapEntityList,
                             MapEntityDetail, MapEntityDelete, MapEntityViewSet,
                             MapEntityFormat, MapEntityDocument)
from mapentity.serializers import plain_text
from rest_framework import generics as rest_generics
from rest_framework import permissions as rest_permissions

from geotrek.authent.decorators import same_structure_required
from geotrek.common.views import DocumentPublic
from geotrek.tourism.models import DataSource, InformationDesk

from .filters import TouristicContentFilterSet, TouristicEventFilterSet
from .forms import TouristicContentForm, TouristicEventForm
from .helpers import post_process
from .models import TouristicContent, TouristicEvent, TouristicContentCategory
from .serializers import (TouristicContentCategorySerializer,
                          TouristicContentSerializer, TouristicEventSerializer)


logger = logging.getLogger(__name__)


class DataSourceList(JSONResponseMixin, ListView):
    model = DataSource

    def get_context_data(self):
        results = []
        for ds in self.get_queryset():
            results.append({
                'id': ds.id,
                'title': ds.title,
                'url': ds.url,
                'type': ds.type,
                'pictogram_url': ds.pictogram.url,
                'geojson_url': ds.get_absolute_url(),
                'targets': ds.targets
            })
        return results

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(DataSourceList, self).dispatch(*args, **kwargs)


class DataSourceGeoJSON(JSONResponseMixin, DetailView):
    model = DataSource

    def get_context_data(self, *args, **kwargs):
        source = self.get_object()

        default_result = geojson.FeatureCollection(features=[])

        try:
            response = requests.get(source.url)
        except RequestException as e:
            logger.error(u"Source '%s' cannot be downloaded" % source.url)
            logger.exception(e)
            return default_result

        try:
            return post_process(source, self.request.LANGUAGE_CODE, response.text)
        except (ValueError, AssertionError) as e:
            return default_result

    @method_decorator(login_required)
    @method_decorator(cache_page(settings.CACHE_TIMEOUT_TOURISM_DATASOURCES, cache="fat"))
    def dispatch(self, *args, **kwargs):
        return super(DataSourceGeoJSON, self).dispatch(*args, **kwargs)


class InformationDeskGeoJSON(GeoJSONLayerView):
    model = InformationDesk
    srid = settings.API_SRID
    properties = {
        'id': 'id',
        'name': 'name',
        'description': 'description',
        'photo_url': 'photo_url',
        'phone': 'phone',
        'email': 'email',
        'website': 'website',
        'street': 'street',
        'postal_code': 'postal_code',
        'municipality': 'municipality',
        'latitude': 'latitude',
        'longitude': 'longitude',
        'serializable_type': 'type'
    }

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(InformationDeskGeoJSON, self).dispatch(*args, **kwargs)


class TouristicContentCategoryJSONList(rest_generics.ListAPIView):
    model = TouristicContentCategory
    serializer_class = TouristicContentCategorySerializer
    permission_classes = (rest_permissions.IsAuthenticated,)


class TouristicContentLayer(MapEntityLayer):
    queryset = TouristicContent.objects.existing()
    properties = ['name']


class TouristicContentList(MapEntityList):
    queryset = TouristicContent.objects.existing()
    filterform = TouristicContentFilterSet
    columns = ['id', 'name', 'category']

    @property
    def categories_list(self):
        used = TouristicContent.objects.values_list('category__pk')
        return TouristicContentCategory.objects.filter(pk__in=used)


class TouristicContentFormatList(MapEntityFormat, TouristicContentList):
    columns = [
        'id', 'name', 'category', 'type1', 'type2', 'description_teaser',
        'description', 'themes', 'contact', 'email', 'website', 'practical_info',
        'published', 'publication_date',
        'structure', 'date_insert', 'date_update',
        'cities', 'districts', 'areas',
    ]


class TouristicContentDetail(MapEntityDetail):
    queryset = TouristicContent.objects.existing()

    def get_context_data(self, *args, **kwargs):
        context = super(TouristicContentDetail, self).get_context_data(*args, **kwargs)
        context['can_edit'] = self.get_object().same_structure(self.request.user)
        return context


class TouristicContentCreate(MapEntityCreate):
    model = TouristicContent
    form_class = TouristicContentForm

    def get_initial(self):
        """
        Returns the initial data to use for forms on this view.
        """
        initial = super(TouristicContentCreate, self).get_initial()
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
        return super(TouristicContentUpdate, self).dispatch(*args, **kwargs)


class TouristicContentDelete(MapEntityDelete):
    model = TouristicContent

    @same_structure_required('tourism:touristiccontent_detail')
    def dispatch(self, *args, **kwargs):
        return super(TouristicContentDelete, self).dispatch(*args, **kwargs)


class TouristicContentDocument(MapEntityDocument):
    queryset = TouristicContent.objects.existing()


class TouristicContentDocumentPublic(DocumentPublic):
    queryset = TouristicContent.objects.existing()

    def get_context_data(self, **kwargs):
        context = super(TouristicContentDocumentPublic, self).get_context_data(**kwargs)
        content = self.get_object()

        context['headerimage_ratio'] = settings.EXPORT_HEADER_IMAGE_SIZE['touristiccontent']

        # Replace HTML text with plain text
        for attr in ['description', 'description_teaser', 'contact', 'practical_info']:
            setattr(content, attr, plain_text(getattr(content, attr)))

        context['object'] = context['content'] = content

        return context


class TouristicEventLayer(MapEntityLayer):
    queryset = TouristicEvent.objects.existing()
    properties = ['name']


class TouristicEventList(MapEntityList):
    queryset = TouristicEvent.objects.existing()
    filterform = TouristicEventFilterSet
    columns = ['id', 'name', 'type']


class TouristicEventFormatList(MapEntityFormat, TouristicEventList):
    columns = [
        'id', 'name', 'type', 'description_teaser', 'description', 'themes',
        'begin_date', 'end_date', 'duration', 'meeting_point', 'meeting_time',
        'contact', 'email', 'website', 'organizer', 'speaker', 'accessibility',
        'participant_number', 'booking', 'target_audience', 'practical_info',
        'structure', 'date_insert', 'date_update',
        'published', 'publication_date',
        'cities', 'districts', 'areas',
    ]


class TouristicEventDetail(MapEntityDetail):
    queryset = TouristicEvent.objects.existing()

    def get_context_data(self, *args, **kwargs):
        context = super(TouristicEventDetail, self).get_context_data(*args, **kwargs)
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
        return super(TouristicEventUpdate, self).dispatch(*args, **kwargs)


class TouristicEventDelete(MapEntityDelete):
    model = TouristicEvent

    @same_structure_required('tourism:touristicevent_detail')
    def dispatch(self, *args, **kwargs):
        return super(TouristicEventDelete, self).dispatch(*args, **kwargs)


class TouristicEventDocument(MapEntityDocument):
    queryset = TouristicEvent.objects.existing()


class TouristicEventDocumentPublic(DocumentPublic):
    queryset = TouristicEvent.objects.existing()

    def get_context_data(self, **kwargs):
        context = super(TouristicEventDocumentPublic, self).get_context_data(**kwargs)
        event = self.get_object()

        context['headerimage_ratio'] = settings.EXPORT_HEADER_IMAGE_SIZE['touristiccontent']

        # Replace HTML text with plain text
        for attr in ['description', 'description_teaser', 'contact', 'booking', 'practical_info']:
            setattr(event, attr, plain_text(getattr(event, attr)))

        context['object'] = context['event'] = event

        return context


class TouristicContentViewSet(MapEntityViewSet):
    queryset = TouristicContent.objects.existing().transform(settings.API_SRID, field_name='geom')
    serializer_class = TouristicContentSerializer
    permission_classes = [rest_permissions.DjangoModelPermissionsOrAnonReadOnly]


class TouristicEventViewSet(MapEntityViewSet):
    queryset = TouristicEvent.objects.existing().transform(settings.API_SRID, field_name='geom')
    serializer_class = TouristicEventSerializer
    permission_classes = [rest_permissions.DjangoModelPermissionsOrAnonReadOnly]
