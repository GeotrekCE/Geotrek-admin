from datetime import datetime, timedelta
import json
import redis

from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from django.db.models.query import Prefetch
from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.utils import translation
from django.utils.decorators import method_decorator
from django.utils.html import escape
from django.views.generic import CreateView, ListView, RedirectView
from django.views.generic.detail import BaseDetailView
from djcelery.models import TaskMeta
from mapentity.helpers import alphabet_enumeration
from mapentity.views import (MapEntityLayer, MapEntityList, MapEntityJsonList,
                             MapEntityFormat, MapEntityDetail, MapEntityMapImage,
                             MapEntityDocument, MapEntityCreate, MapEntityUpdate,
                             MapEntityDelete, LastModifiedMixin, MapEntityViewSet)
from rest_framework import permissions as rest_permissions, viewsets
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from geotrek.authent.decorators import same_structure_required
from geotrek.common.models import RecordSource, TargetPortal, Attachment
from geotrek.common.views import FormsetMixin, PublicOrReadPermMixin, DocumentPublic
from geotrek.core.models import AltimetryMixin
from geotrek.core.views import CreateFromTopologyMixin
from geotrek.trekking.forms import SyncRandoForm
from geotrek.zoning.models import District, City, RestrictedArea
from geotrek.celery import app as celery_app

from .filters import TrekFilterSet, POIFilterSet, ServiceFilterSet
from .forms import (TrekForm, TrekRelationshipFormSet, POIForm,
                    WebLinkCreateFormPopup, ServiceForm)
from .models import Trek, POI, WebLink, Service, TrekRelationship, OrderedTrekChild
from .serializers import (TrekGPXSerializer, TrekSerializer, POISerializer,
                          CirkwiTrekSerializer, CirkwiPOISerializer, ServiceSerializer)
from .tasks import launch_sync_rando


class SyncRandoRedirect(RedirectView):
    http_method_names = ['post']
    permanent = False
    query_string = False

    @method_decorator(login_required)
    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def post(self, request, *args, **kwargs):
        url = "{scheme}://{host}".format(scheme='https' if self.request.is_secure() else 'http',
                                         host=self.request.get_host())
        self.job = launch_sync_rando.delay(url=url)
        return super(SyncRandoRedirect,
                     self).post(request, *args, **kwargs)

    def get_redirect_url(self, *args, **kwargs):
        self.url = self.request.META.get('HTTP_REFERER')
        return super(SyncRandoRedirect,
                     self).get_redirect_url(*args,
                                            **kwargs)


class FlattenPicturesMixin(object):
    def get_template_names(self):
        """ Due to bug in Django, providing get_queryset() method hides
        template_names lookup.
        https://code.djangoproject.com/ticket/17484
        """
        opts = self.get_model()._meta
        extra = ["%s/%s%s.html" % (opts.app_label, opts.object_name.lower(), self.template_name_suffix)]
        return extra + super(FlattenPicturesMixin, self).get_template_names()

    def get_queryset(self):
        """ Override queryset to avoid attachment lookup while serializing.
        It will fetch attachments, and force ``pictures`` attribute of instances.
        """
        app_label = self.get_model()._meta.app_label
        model_name = self.get_model()._meta.object_name.lower()
        attachments = Attachment.objects.filter(content_type__app_label=app_label,
                                                content_type__model=model_name)
        pictures = {}
        for attachment in attachments:
            if attachment.is_image:
                obj_id = attachment.object_id
                pictures.setdefault(obj_id, []).append(attachment)

        for obj in super(FlattenPicturesMixin, self).get_queryset():
            obj.pictures = pictures.get(obj.id, [])
            yield obj


class TrekLayer(MapEntityLayer):
    properties = ['name', 'published']
    queryset = Trek.objects.existing()


class TrekList(FlattenPicturesMixin, MapEntityList):
    queryset = Trek.objects.existing()
    filterform = TrekFilterSet
    columns = ['id', 'name', 'duration', 'difficulty', 'departure', 'thumbnail']


class TrekJsonList(MapEntityJsonList, TrekList):
    pass


class TrekFormatList(MapEntityFormat, TrekList):
    columns = [
        'id', 'eid', 'eid2', 'name', 'departure', 'arrival', 'duration',
        'duration_pretty', 'description', 'description_teaser',
        'networks', 'advice', 'ambiance', 'difficulty', 'information_desks',
        'themes', 'practice', 'accessibilities', 'access', 'route',
        'public_transport', 'advised_parking', 'web_links', 'is_park_centered',
        'disabled_infrastructure', 'parking_location', 'points_reference',
        'related', 'children', 'parents', 'pois', 'review', 'published',
        'publication_date', 'structure', 'date_insert', 'date_update',
        'cities', 'districts', 'areas', 'source', 'portal', 'length_2d'
    ] + AltimetryMixin.COLUMNS


class TrekGPXDetail(LastModifiedMixin, PublicOrReadPermMixin, BaseDetailView):
    queryset = Trek.objects.existing()

    def render_to_response(self, context):
        gpx_serializer = TrekGPXSerializer()
        response = HttpResponse(content_type='application/gpx+xml')
        response['Content-Disposition'] = 'attachment; filename=%s.gpx' % self.get_object().slug
        gpx_serializer.serialize([self.get_object()], stream=response, geom_field='geom')
        return response


class TrekKMLDetail(LastModifiedMixin, PublicOrReadPermMixin, BaseDetailView):
    queryset = Trek.objects.existing()

    def render_to_response(self, context):
        trek = self.get_object()
        response = HttpResponse(trek.kml(),
                                content_type='application/vnd.google-earth.kml+xml')
        return response


class TrekDetail(MapEntityDetail):
    queryset = Trek.objects.existing()

    @property
    def icon_sizes(self):
        return {
            'POI': settings.TREK_ICON_SIZE_POI,
            'service': settings.TREK_ICON_SIZE_SERVICE,
            'parking': settings.TREK_ICON_SIZE_PARKING,
            'information_desk': settings.TREK_ICON_SIZE_INFORMATION_DESK
        }

    def dispatch(self, *args, **kwargs):
        lang = self.request.GET.get('lang')
        if lang:
            translation.activate(lang)
            self.request.LANGUAGE_CODE = lang
        return super(TrekDetail, self).dispatch(*args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super(TrekDetail, self).get_context_data(*args, **kwargs)
        context['can_edit'] = self.get_object().same_structure(self.request.user)
        return context


class TrekMapImage(MapEntityMapImage):
    queryset = Trek.objects.existing()

    def dispatch(self, *args, **kwargs):
        lang = kwargs.pop('lang')
        if lang:
            translation.activate(lang)
            self.request.LANGUAGE_CODE = lang
        return super(TrekMapImage, self).dispatch(*args, **kwargs)


class TrekDocument(MapEntityDocument):
    queryset = Trek.objects.existing()


class TrekDocumentPublicBase(DocumentPublic):
    queryset = Trek.objects.existing()

    def get_context_data(self, **kwargs):
        context = super(TrekDocumentPublicBase, self).get_context_data(**kwargs)
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


class TrekDocumentPublic(TrekDocumentPublicBase):

    def render_to_response(self, context, **response_kwargs):
        # Prepare altimetric graph
        trek = self.get_object()
        language = self.request.LANGUAGE_CODE
        trek.prepare_elevation_chart(language, self.request.build_absolute_uri('/'))
        return super(TrekDocumentPublic, self).render_to_response(context, **response_kwargs)


class TrekRelationshipFormsetMixin(FormsetMixin):
    context_name = 'relationship_formset'
    formset_class = TrekRelationshipFormSet


class TrekCreate(TrekRelationshipFormsetMixin, CreateFromTopologyMixin, MapEntityCreate):
    model = Trek
    form_class = TrekForm


class TrekUpdate(TrekRelationshipFormsetMixin, MapEntityUpdate):
    queryset = Trek.objects.existing()
    form_class = TrekForm

    @same_structure_required('trekking:trek_detail')
    def dispatch(self, *args, **kwargs):
        return super(TrekUpdate, self).dispatch(*args, **kwargs)


class TrekDelete(MapEntityDelete):
    model = Trek

    @same_structure_required('trekking:trek_detail')
    def dispatch(self, *args, **kwargs):
        return super(TrekDelete, self).dispatch(*args, **kwargs)


class POILayer(MapEntityLayer):
    queryset = POI.objects.existing()
    properties = ['name', 'published']


class POIList(FlattenPicturesMixin, MapEntityList):
    queryset = POI.objects.existing()
    filterform = POIFilterSet
    columns = ['id', 'name', 'type', 'thumbnail']


class POIJsonList(MapEntityJsonList, POIList):
    pass


class POIFormatList(MapEntityFormat, POIList):
    columns = [
        'id', 'eid', 'name', 'type', 'description', 'treks',
        'review', 'published', 'publication_date',
        'structure', 'date_insert', 'date_update',
        'cities', 'districts', 'areas'
    ] + AltimetryMixin.COLUMNS

    set(POIList.columns + ['description', 'treks', 'districts', 'cities', 'areas', 'structure'])

    def get_queryset(self):
        qs = super(POIFormatList, self).get_queryset()

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
                    denormalized[attrname].setdefault(pid, []).append(d)

        # Same for treks
        denormalized['treks'] = {}
        for d in Trek.objects.existing():
            for pid in d.pois.all():
                denormalized['treks'].setdefault(pid, []).append(d)

        for poi in qs:
            # Put denormalized in specific attribute used in serializers
            for attrname in denormalized.keys():
                overlapping = denormalized[attrname].get(poi.id, [])
                setattr(poi, '%s_csv_display' % attrname, overlapping)
            yield poi


class POIDetail(MapEntityDetail):
    queryset = POI.objects.existing()

    def get_context_data(self, *args, **kwargs):
        context = super(POIDetail, self).get_context_data(*args, **kwargs)
        context['can_edit'] = self.get_object().same_structure(self.request.user)
        return context


class POIDocument(MapEntityDocument):
    model = POI


class POIDocumentPublic(DocumentPublic):
    queryset = POI.objects.existing()

    def get_context_data(self, **kwargs):
        context = super(POIDocumentPublic, self).get_context_data(**kwargs)
        context['headerimage_ratio'] = settings.EXPORT_HEADER_IMAGE_SIZE['poi']
        return context


class POICreate(MapEntityCreate):
    model = POI
    form_class = POIForm


class POIUpdate(MapEntityUpdate):
    queryset = POI.objects.existing()
    form_class = POIForm

    @same_structure_required('trekking:poi_detail')
    def dispatch(self, *args, **kwargs):
        return super(POIUpdate, self).dispatch(*args, **kwargs)


class POIDelete(MapEntityDelete):
    model = POI

    @same_structure_required('trekking:poi_detail')
    def dispatch(self, *args, **kwargs):
        return super(POIDelete, self).dispatch(*args, **kwargs)


class WebLinkCreatePopup(CreateView):
    model = WebLink
    form_class = WebLinkCreateFormPopup

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(WebLinkCreatePopup, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        self.object = form.save()
        return HttpResponse("""
            <script type="text/javascript">opener.dismissAddAnotherPopup(window, "%s", "%s");</script>
        """ % (escape(form.instance._get_pk_val()), escape(form.instance)))


class TrekViewSet(MapEntityViewSet):
    model = Trek
    serializer_class = TrekSerializer
    permission_classes = [rest_permissions.DjangoModelPermissionsOrAnonReadOnly]

    def get_queryset(self):
        qs = self.model.objects.existing()
        qs = qs.select_related('structure',)
        qs = qs.prefetch_related(
            'networks', 'source', 'portal', 'web_links', 'accessibilities', 'themes', 'aggregations',
            'information_desks',
            Prefetch('trek_relationship_a', queryset=TrekRelationship.objects.select_related('trek_a', 'trek_b')),
            Prefetch('trek_relationship_b', queryset=TrekRelationship.objects.select_related('trek_a', 'trek_b')),
            Prefetch('trek_children', queryset=OrderedTrekChild.objects.select_related('parent', 'child')),
            Prefetch('trek_parents', queryset=OrderedTrekChild.objects.select_related('parent', 'child')),
        )
        qs = qs.filter(Q(published=True) | Q(trek_parents__parent__published=True))\
               .order_by('pk').distinct('pk')

        if 'source' in self.request.GET:
            qs = qs.filter(source__name__in=self.request.GET['source'].split(','))

        if 'portal' in self.request.GET:
            qs = qs.filter(portal__name__in=self.request.GET['portal'].split(','))

        qs = qs.transform(settings.API_SRID, field_name='geom')

        return qs


class POIViewSet(MapEntityViewSet):
    model = POI
    serializer_class = POISerializer
    permission_classes = [rest_permissions.DjangoModelPermissionsOrAnonReadOnly]

    def get_queryset(self):
        return POI.objects.existing().filter(published=True).transform(settings.API_SRID, field_name='geom')


class TrekPOIViewSet(viewsets.ModelViewSet):
    model = POI
    permission_classes = [rest_permissions.DjangoModelPermissionsOrAnonReadOnly]

    def get_serializer_class(self):
        class Serializer(POISerializer, GeoFeatureModelSerializer):
            pass
        return Serializer

    def get_queryset(self):
        pk = self.kwargs['pk']
        try:
            trek = Trek.objects.existing().get(pk=pk)
        except Trek.DoesNotExist:
            raise Http404
        if not trek.is_public:
            raise Http404
        return trek.pois.filter(published=True).transform(settings.API_SRID, field_name='geom')


class ServiceLayer(MapEntityLayer):
    properties = ['label', 'published']
    queryset = Service.objects.existing()


class ServiceList(MapEntityList):
    filterform = ServiceFilterSet
    columns = ['id', 'name']
    queryset = Service.objects.existing()


class ServiceJsonList(MapEntityJsonList, ServiceList):
    pass


class ServiceFormatList(MapEntityFormat, ServiceList):
    columns = [
        'id', 'eid', 'type'
    ] + AltimetryMixin.COLUMNS


class ServiceDetail(MapEntityDetail):
    queryset = Service.objects.existing()

    def get_context_data(self, *args, **kwargs):
        context = super(ServiceDetail, self).get_context_data(*args, **kwargs)
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
        return super(ServiceUpdate, self).dispatch(*args, **kwargs)


class ServiceDelete(MapEntityDelete):
    model = Service

    @same_structure_required('trekking:service_detail')
    def dispatch(self, *args, **kwargs):
        return super(ServiceDelete, self).dispatch(*args, **kwargs)


class ServiceViewSet(MapEntityViewSet):
    model = Service
    serializer_class = ServiceSerializer
    permission_classes = [rest_permissions.DjangoModelPermissionsOrAnonReadOnly]

    def get_queryset(self):
        return Service.objects.existing().filter(type__published=True).transform(settings.API_SRID, field_name='geom')


class TrekServiceViewSet(viewsets.ModelViewSet):
    model = Service
    permission_classes = [rest_permissions.DjangoModelPermissionsOrAnonReadOnly]

    def get_serializer_class(self):
        class Serializer(ServiceSerializer, GeoFeatureModelSerializer):
            pass
        return Serializer

    def get_queryset(self):
        pk = self.kwargs['pk']
        try:
            trek = Trek.objects.existing().get(pk=pk)
        except Trek.DoesNotExist:
            raise Http404
        if not trek.is_public:
            raise Http404
        return trek.services.filter(type__published=True).transform(settings.API_SRID, field_name='geom')


class CirkwiTrekView(ListView):
    model = Trek

    def get_queryset(self):
        qs = Trek.objects.existing()
        qs = qs.filter(published=True)
        return qs

    def get(self, request):
        response = HttpResponse(content_type='application/xml')
        serializer = CirkwiTrekSerializer(request, response, request.GET)
        treks = self.get_queryset()
        serializer.serialize(treks)
        return response


class CirkwiPOIView(ListView):
    model = POI

    def get_queryset(self):
        qs = POI.objects.existing()
        qs = qs.filter(published=True)
        return qs

    def get(self, request):
        response = HttpResponse(content_type='application/xml')
        serializer = CirkwiPOISerializer(request, response)
        pois = self.get_queryset()
        serializer.serialize(pois)
        return response


@login_required
@user_passes_test(lambda u: u.is_superuser)
def sync_view(request):
    """
    Custom views to view / track / launch a sync rando
    """

    return render_to_response(
        'trekking/sync_rando.html',
        {'form': SyncRandoForm(), },
        context_instance=RequestContext(request)
    )


@login_required
@user_passes_test(lambda u: u.is_superuser)
def sync_update_json(request):
    """
    get info from sync_rando celery_task
    """
    results = []
    threshold = datetime.now() - timedelta(seconds=60)
    for task in TaskMeta.objects.filter(date_done__gte=threshold, status='PROGRESS'):
        if (hasattr(task, 'result') and
                'name' in task.result and
                task.result.get('name', '').startswith('geotrek.trekking')):
            results.append({
                'id': task.task_id,
                'result': task.result or {'current': 0,
                                          'total': 0},
                'status': task.status
            })
    i = celery_app.control.inspect([u'celery@geotrek'])
    try:
        reserved = i.reserved()
    except redis.exceptions.ConnectionError:
        reserved = None
    tasks = [] if reserved is None else reversed(reserved[u'celery@geotrek'])
    for task in tasks:
        if task['name'].startswith('geotrek.trekking'):
            results.append(
                {
                    'id': task['id'],
                    'result': {'current': 0, 'total': 0},
                    'status': 'PENDING',
                }
            )
    for task in TaskMeta.objects.filter(date_done__gte=threshold, status='FAILURE').order_by('-date_done'):
        if (hasattr(task, 'result') and
                'name' in task.result and
                task.result.get('name', '').startswith('geotrek.trekking')):
            results.append({
                'id': task.task_id,
                'result': task.result or {'current': 0,
                                          'total': 0},
                'status': task.status
            })

    return HttpResponse(json.dumps(results),
                        content_type="application/json")


# Translations for public PDF
translation.ugettext_noop(u"Advices")
translation.ugettext_noop(u"All useful information")
translation.ugettext_noop(u"Altimetric profile")
translation.ugettext_noop(u"Attribution")
translation.ugettext_noop(u"Geographical location")
translation.ugettext_noop(u"Markings")
translation.ugettext_noop(u"Max elevation")
translation.ugettext_noop(u"Min elevation")
translation.ugettext_noop(u"On your path...")
translation.ugettext_noop(u"Powered by geotrek.fr")
translation.ugettext_noop(u"The national park is an unrestricted natural area but subjected to regulations which must be known by all visitors.")
translation.ugettext_noop(u"This hike is in the core of the national park")
translation.ugettext_noop(u"Trek ascent")
translation.ugettext_noop(u"Useful information")
