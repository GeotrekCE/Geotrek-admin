from django.conf import settings
from django.http import HttpResponse, Http404
from django.utils.decorators import method_decorator
from django.utils.html import escape
from django.utils import translation
from django.views.generic.edit import CreateView
from django.views.generic.detail import BaseDetailView
from django.contrib.auth.decorators import login_required

from djgeojson.views import GeoJSONLayerView
from mapentity.views import (MapEntityLayer, MapEntityList, MapEntityJsonList, MapEntityFormat,
                             MapEntityDetail, MapEntityMapImage, MapEntityDocument, MapEntityCreate, MapEntityUpdate, MapEntityDelete,
                             LastModifiedMixin, MapEntityViewSet)
from mapentity.serializers import plain_text
from mapentity.helpers import alphabet_enumeration
from paperclip.models import Attachment
from rest_framework import permissions as rest_permissions

from geotrek.core.views import CreateFromTopologyMixin

from geotrek.common.views import FormsetMixin, DocumentPublic
from geotrek.zoning.models import District, City, RestrictedArea
from geotrek.tourism.views import InformationDeskGeoJSON

from .models import Trek, POI, WebLink
from .filters import TrekFilterSet, POIFilterSet
from .forms import TrekForm, TrekRelationshipFormSet, POIForm, WebLinkCreateFormPopup
from .serializers import TrekGPXSerializer, TrekSerializer, POISerializer


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
    columns = (
        'id', 'name', 'departure', 'arrival', 'duration',
        'duration_pretty', 'description', 'description_teaser',
        'networks', 'advice', 'ambiance', 'difficulty',
        'information_desks', 'themes', 'practice', 'access',
        'route', 'public_transport', 'advised_parking',
        'web_links', 'is_park_centered', 'disabled_infrastructure',
        'parking_location', 'points_reference', 'related', 'pois',
    )


class TrekGPXDetail(LastModifiedMixin, BaseDetailView):
    queryset = Trek.objects.existing()

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(TrekGPXDetail, self).dispatch(*args, **kwargs)

    def render_to_response(self, context):
        gpx_serializer = TrekGPXSerializer()
        response = HttpResponse(mimetype='application/gpx+xml')
        response['Content-Disposition'] = 'attachment; filename=trek-%s.gpx' % self.get_object().pk
        gpx_serializer.serialize([self.get_object()], stream=response, geom_field='geom')
        return response


class TrekKMLDetail(LastModifiedMixin, BaseDetailView):
    queryset = Trek.objects.existing()

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(TrekKMLDetail, self).dispatch(*args, **kwargs)

    def render_to_response(self, context):
        trek = self.get_object()
        response = HttpResponse(trek.kml(),
                                content_type='application/vnd.google-earth.kml+xml')
        return response


class TrekPOIGeoJSON(LastModifiedMixin, GeoJSONLayerView):
    model = Trek  # for LastModifiedMixin
    srid = settings.API_SRID
    pk_url_kwarg = 'pk'
    properties = {'pk': 'pk', 'name': 'name', 'description': 'description',
                  'max_elevation': 'elevation', 'serializable_thumbnail': 'thumbnail',
                  'serializable_type': 'type', 'serializable_pictures': 'pictures'}

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(TrekPOIGeoJSON, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        try:
            trek_pk = self.kwargs.get(self.pk_url_kwarg)
            trek = Trek.objects.get(pk=trek_pk)
        except Trek.DoesNotExist:
            raise Http404
        # All published POIs for this trek
        return trek.pois.filter(published=True).select_related('type')


class TrekInformationDeskGeoJSON(LastModifiedMixin, GeoJSONLayerView):
    model = Trek
    srid = settings.API_SRID
    pk_url_kwarg = 'pk'

    properties = InformationDeskGeoJSON.properties

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(TrekInformationDeskGeoJSON, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        try:
            trek_pk = self.kwargs.get(self.pk_url_kwarg)
            trek = Trek.objects.get(pk=trek_pk)
        except Trek.DoesNotExist:
            raise Http404
        return trek.information_desks.all()


class TrekDetail(MapEntityDetail):
    queryset = Trek.objects.existing()

    @property
    def icon_sizes(self):
        return {
            'POI': settings.TREK_ICON_SIZE_POI,
            'parking': settings.TREK_ICON_SIZE_PARKING,
            'information_desk': settings.TREK_ICON_SIZE_INFORMATION_DESK
        }

    def dispatch(self, *args, **kwargs):
        lang = self.request.GET.get('lang')
        if lang:
            translation.activate(lang)
            self.request.LANGUAGE_CODE = lang
        return super(TrekDetail, self).dispatch(*args, **kwargs)


class TrekMapImage(MapEntityMapImage):
    queryset = Trek.objects.existing()


class TrekDocument(MapEntityDocument):
    queryset = Trek.objects.existing()


class TrekDocumentPublic(DocumentPublic):
    queryset = Trek.objects.existing()

    def get_context_data(self, **kwargs):
        context = super(TrekDocumentPublic, self).get_context_data(**kwargs)
        trek = self.get_object()

        context['headerimage_ratio'] = settings.EXPORT_HEADER_IMAGE_SIZE['trek']

        information_desks = list(trek.information_desks.all())
        if settings.TREK_EXPORT_INFORMATION_DESK_LIST_LIMIT > 0:
            information_desks = information_desks[:settings.TREK_EXPORT_INFORMATION_DESK_LIST_LIMIT]
        context['information_desks'] = information_desks

        pois = list(trek.pois.filter(published=True))
        if settings.TREK_EXPORT_POI_LIST_LIMIT > 0:
            pois = pois[:settings.TREK_EXPORT_POI_LIST_LIMIT]
        context['pois'] = pois

        # Replace HTML text with plain text
        for attr in ['description', 'description_teaser', 'ambiance', 'advice', 'access',
                     'public_transport', 'advised_parking', 'disabled_infrastructure']:
            setattr(trek, attr, plain_text(getattr(trek, attr)))

        for poi in context['pois']:
            setattr(poi, 'description', plain_text(getattr(poi, 'description')))

        #
        # POIs enumeration, like shown on the map
        # https://github.com/makinacorpus/Geotrek/issues/871
        enumeration = {}
        letters = alphabet_enumeration(len(trek.pois))
        for i, p in enumerate(trek.pois):
            enumeration[p.pk] = letters[i]
        context['enumeration'] = enumeration

        context['object'] = context['trek'] = trek

        return context

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


class TrekDelete(MapEntityDelete):
    model = Trek


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
    columns = set(POIList.columns + ['description', 'treks', 'districts', 'cities', 'areas'])

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


class POIDelete(MapEntityDelete):
    model = POI


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
    queryset = Trek.objects.existing().transform(settings.API_SRID, field_name='geom')
    serializer_class = TrekSerializer
    permission_classes = [rest_permissions.DjangoModelPermissionsOrAnonReadOnly]


class POIViewSet(MapEntityViewSet):
    queryset = POI.objects.existing().transform(settings.API_SRID, field_name='geom')
    serializer_class = POISerializer
    permission_classes = [rest_permissions.DjangoModelPermissionsOrAnonReadOnly]
