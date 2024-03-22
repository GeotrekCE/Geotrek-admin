from django.conf import settings
from django.contrib.gis.db.models.functions import Transform
from django.utils import translation
from mapentity.views import (MapEntityList, MapEntityFormat, MapEntityDetail, MapEntityMapImage,
                             MapEntityDocument, MapEntityCreate, MapEntityUpdate, MapEntityDelete)

from geotrek.authent.decorators import same_structure_required
from geotrek.common.mixins.views import CompletenessMixin, CustomColumnsMixin
from geotrek.common.models import RecordSource, TargetPortal
from geotrek.common.views import DocumentPublic, DocumentBookletPublic, MarkupPublic
from geotrek.common.viewsets import GeotrekMapentityViewSet
from geotrek.trekking.views import FlattenPicturesMixin
from .filters import DiveFilterSet
from .forms import DiveForm
from .models import Dive
from .serializers import DiveSerializer, DiveGeojsonSerializer


class DiveList(CustomColumnsMixin, FlattenPicturesMixin, MapEntityList):
    filterform = DiveFilterSet
    queryset = Dive.objects.existing()
    mandatory_columns = ['id', 'name']
    default_extra_columns = ['levels', 'thumbnail']
    unorderable_columns = ['thumbnail']
    searchable_columns = ['id', 'name']


class DiveFormatList(MapEntityFormat, DiveList):
    mandatory_columns = ['id']
    default_extra_columns = [
        'eid', 'structure', 'name', 'departure',
        'description', 'description_teaser',
        'advice', 'difficulty', 'levels',
        'themes', 'practice', 'disabled_sport',
        'published', 'publication_date', 'date_insert', 'date_update',
        'areas', 'source', 'portal', 'review'
    ]


class DiveDetail(CompletenessMixin, MapEntityDetail):
    queryset = Dive.objects.existing()

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


class DiveMapImage(MapEntityMapImage):
    queryset = Dive.objects.existing()

    def dispatch(self, *args, **kwargs):
        lang = kwargs.pop('lang')
        if lang:
            translation.activate(lang)
            self.request.LANGUAGE_CODE = lang
        return super().dispatch(*args, **kwargs)


class DiveDocument(MapEntityDocument):
    queryset = Dive.objects.existing()


class DiveDocumentPublicMixin:
    queryset = Dive.objects.existing()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dive = self.get_object()

        context['headerimage_ratio'] = settings.EXPORT_HEADER_IMAGE_SIZE['dive']

        context['object'] = context['dive'] = dive
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


class DiveDocumentPublic(DiveDocumentPublicMixin, DocumentPublic):
    pass


class DiveDocumentBookletPublic(DiveDocumentPublicMixin, DocumentBookletPublic):
    pass


class DiveMarkupPublic(DiveDocumentPublicMixin, MarkupPublic):
    pass


class DiveCreate(MapEntityCreate):
    model = Dive
    form_class = DiveForm


class DiveUpdate(MapEntityUpdate):
    queryset = Dive.objects.existing()
    form_class = DiveForm

    @same_structure_required('diving:dive_detail')
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class DiveDelete(MapEntityDelete):
    model = Dive

    @same_structure_required('diving:dive_detail')
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class DiveViewSet(GeotrekMapentityViewSet):
    model = Dive
    serializer_class = DiveSerializer
    geojson_serializer_class = DiveGeojsonSerializer
    filterset_class = DiveFilterSet
    mapentity_list_class = DiveList

    def get_queryset(self):
        qs = self.model.objects.existing()
        if self.format_kwarg == 'geojson':
            qs = qs.annotate(api_geom=Transform('geom', settings.API_SRID))
            qs = qs.only('id', 'name', 'published')

        return qs
