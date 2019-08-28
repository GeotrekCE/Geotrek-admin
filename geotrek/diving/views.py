from urlparse import urljoin

from django.conf import settings
from django.db.models import Q
from django.utils import translation
from django.views.generic import DetailView
from mapentity.views import (MapEntityLayer, MapEntityList, MapEntityJsonList,
                             MapEntityFormat, MapEntityDetail, MapEntityMapImage,
                             MapEntityDocument, MapEntityCreate, MapEntityUpdate,
                             MapEntityDelete, MapEntityViewSet)
from rest_framework import permissions as rest_permissions

from geotrek.authent.decorators import same_structure_required
from geotrek.common.models import RecordSource, TargetPortal
from geotrek.common.views import DocumentPublic, MarkupPublic

from .filters import DiveFilterSet
from .forms import DiveForm
from .models import Dive
from .serializers import DiveSerializer
from geotrek.trekking.views import FlattenPicturesMixin


class DiveLayer(MapEntityLayer):
    properties = ['name', 'published']
    queryset = Dive.objects.existing()


class DiveList(FlattenPicturesMixin, MapEntityList):
    queryset = Dive.objects.existing()
    filterform = DiveFilterSet
    columns = ['id', 'name', 'levels', 'thumbnail']


class DiveJsonList(MapEntityJsonList, DiveList):
    pass


class DiveFormatList(MapEntityFormat, DiveList):
    columns = [
        'id', 'eid', 'structure', 'name', 'departure',
        'description', 'description_teaser',
        'advice', 'difficulty', 'levels',
        'themes', 'practice', 'disabled_sport',
        'published', 'publication_date', 'date_insert', 'date_update',
        'areas', 'source', 'portal',
    ]


class DiveDetail(MapEntityDetail):
    queryset = Dive.objects.existing()

    def dispatch(self, *args, **kwargs):
        lang = self.request.GET.get('lang')
        if lang:
            translation.activate(lang)
            self.request.LANGUAGE_CODE = lang
        return super(DiveDetail, self).dispatch(*args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super(DiveDetail, self).get_context_data(*args, **kwargs)
        context['can_edit'] = self.get_object().same_structure(self.request.user)
        return context


class DiveMapImage(MapEntityMapImage):
    queryset = Dive.objects.existing()

    def dispatch(self, *args, **kwargs):
        lang = kwargs.pop('lang')
        if lang:
            translation.activate(lang)
            self.request.LANGUAGE_CODE = lang
        return super(DiveMapImage, self).dispatch(*args, **kwargs)


class DiveDocument(MapEntityDocument):
    queryset = Dive.objects.existing()


class DiveDocumentPublicMixin(object):
    queryset = Dive.objects.existing()

    def get_context_data(self, **kwargs):
        context = super(DiveDocumentPublicMixin, self).get_context_data(**kwargs)
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
        return super(DiveUpdate, self).dispatch(*args, **kwargs)


class DiveDelete(MapEntityDelete):
    model = Dive

    @same_structure_required('diving:dive_detail')
    def dispatch(self, *args, **kwargs):
        return super(DiveDelete, self).dispatch(*args, **kwargs)


class DiveMeta(DetailView):
    model = Dive
    template_name = 'diving/dive_meta.html'

    def get_context_data(self, **kwargs):
        context = super(DiveMeta, self).get_context_data(**kwargs)
        context['FACEBOOK_APP_ID'] = settings.FACEBOOK_APP_ID
        context['facebook_image'] = urljoin(self.request.GET['rando_url'], settings.FACEBOOK_IMAGE)
        context['FACEBOOK_IMAGE_WIDTH'] = settings.FACEBOOK_IMAGE_WIDTH
        context['FACEBOOK_IMAGE_HEIGHT'] = settings.FACEBOOK_IMAGE_HEIGHT
        return context


class DiveViewSet(MapEntityViewSet):
    model = Dive
    serializer_class = DiveSerializer
    permission_classes = [rest_permissions.DjangoModelPermissionsOrAnonReadOnly]

    def get_queryset(self):
        qs = self.model.objects.existing()
        qs = qs.select_related('structure', 'difficulty', 'practice')
        qs = qs.prefetch_related('levels', 'source', 'portal', 'themes', 'attachments')
        qs = qs.filter(published=True).order_by('pk').distinct('pk')
        if 'source' in self.request.GET:
            qs = qs.filter(source__name__in=self.request.GET['source'].split(','))

        if 'portal' in self.request.GET:
            qs = qs.filter(Q(portal__name__in=self.request.GET['portal'].split(',')) | Q(portal=None))

        qs = qs.transform(settings.API_SRID, field_name='geom')

        return qs


# Translations for public PDF
# translation.ugettext_noop(u"...")
