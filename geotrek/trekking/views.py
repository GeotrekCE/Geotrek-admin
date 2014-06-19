from django.conf import settings
from django.http import HttpResponse, Http404
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.utils.decorators import method_decorator
from django.utils.html import escape
from django.utils import translation
from django.views.generic.edit import CreateView
from django.views.generic.detail import BaseDetailView
from django.contrib.auth.decorators import login_required

from djgeojson.views import GeoJSONLayerView
from mapentity.views import (MapEntityLayer, MapEntityList, MapEntityJsonList, MapEntityFormat,
                             MapEntityDetail, MapEntityMapImage, MapEntityDocument, MapEntityCreate, MapEntityUpdate, MapEntityDelete,
                             LastModifiedMixin, JSONResponseMixin, DocumentConvert)
from mapentity.serializers import plain_text
from paperclip.models import Attachment

from geotrek.core.views import CreateFromTopologyMixin
from geotrek.core.models import AltimetryMixin
from geotrek.common.views import FormsetMixin
from geotrek.zoning.models import District, City, RestrictedArea

from .models import Trek, POI, WebLink
from .filters import TrekFilterSet, POIFilterSet
from .forms import TrekForm, TrekRelationshipFormSet, POIForm, WebLinkCreateFormPopup
from .serializers import TrekGPXSerializer


class FlattenPicturesMixin(object):
    def get_template_names(self):
        """ Due to bug in Django, providing get_queryset() method hides
        template_names lookup.
        https://code.djangoproject.com/ticket/17484
        """
        opts = self.model._meta
        extra = ["%s/%s%s.html" % (opts.app_label, opts.object_name.lower(), self.template_name_suffix)]
        return extra + super(FlattenPicturesMixin, self).get_template_names()

    def get_queryset(self):
        """ Override queryset to avoid attachment lookup while serializing.
        It will fetch attachments, and force ``pictures`` attribute of instances.
        """
        app_label = self.model._meta.app_label
        model_name = self.model._meta.object_name.lower()
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


class TrekJsonDetail(LastModifiedMixin, JSONResponseMixin, BaseDetailView):
    queryset = Trek.objects.existing()
    columns = ['name', 'slug', 'departure', 'arrival', 'duration', 'duration_pretty', 'description',
               'description_teaser'] + AltimetryMixin.COLUMNS + ['published',
               'networks', 'advice', 'ambiance', 'difficulty',
               'information_desks', 'information_desk',  # singular: retro-compat
               'themes', 'usages', 'access', 'route', 'public_transport', 'advised_parking',
               'web_links', 'is_park_centered', 'disabled_infrastructure',
               'parking_location', 'thumbnail', 'pictures',
               'cities', 'districts', 'relationships', 'map_image_url',
               'elevation_area_url']

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(TrekJsonDetail, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = {}
        for fname in self.columns:
            ctx[fname] = getattr(self.object, 'serializable_%s' % fname,
                                 getattr(self.object, fname))

        trek = self.get_object()
        ctx['altimetric_profile'] = reverse('trekking:trek_profile', args=(trek.pk,))
        ctx['poi_layer'] = reverse('trekking:trek_poi_geojson', args=(trek.pk,))
        ctx['information_desk_layer'] = reverse('trekking:trek_information_desk_geojson', args=(trek.pk,))
        ctx['filelist_url'] = reverse('paperclip:get_attachments',
                                      kwargs={'app_label': 'trekking',
                                              'module_name': 'trek',
                                              'pk': trek.pk})
        ctx['gpx'] = reverse('trekking:trek_gpx_detail', args=(trek.pk,))
        ctx['kml'] = reverse('trekking:trek_kml_detail', args=(trek.pk,))
        ctx['printable'] = reverse('trekking:trek_printable', args=(trek.pk,))
        return ctx


class TrekFormatList(MapEntityFormat, TrekList):
    columns = set(TrekList.columns + TrekJsonDetail.columns + ['related', 'pois']) - set(['relationships', 'thumbnail', 'map_image_url', 'slug'])


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
    properties = {'pk':'pk', 'name':'name', 'description':'description',
                  'max_elevation':'elevation', 'serializable_thumbnail':'thumbnail',
                  'serializable_type':'type', 'serializable_pictures':'pictures'}

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(TrekPOIGeoJSON, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        try:
            trek_pk = self.kwargs.get(self.pk_url_kwarg)
            trek = Trek.objects.get(pk=trek_pk)
        except Trek.DoesNotExist:
            raise Http404
        # All POIs of this trek
        return trek.pois.select_related('type')


class TrekInformationDeskGeoJSON(LastModifiedMixin, GeoJSONLayerView):
    model = Trek
    srid = settings.API_SRID
    pk_url_kwarg = 'pk'

    properties = ['id', 'name', 'description', 'photo_url', 'phone',
                  'email', 'website', 'street', 'postal_code', 'municipality',
                  'latitude', 'longitude']

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

    def dispatch(self, *args, **kwargs):
        lang = self.request.GET.get('lang')
        if lang:
            translation.activate(lang)
            self.request.LANGUAGE_CODE = lang
        return super(TrekDetail, self).dispatch(*args, **kwargs)


class TrekMapImage(MapEntityMapImage):
    model = Trek


class TrekDocument(MapEntityDocument):
    model = Trek


class TrekDocumentPublic(TrekDocument):
    template_name_suffix = "_public"

    def get_context_data(self, **kwargs):
        context = super(TrekDocumentPublic, self).get_context_data(**kwargs)
        # Replace HTML text with plain text
        trek = self.get_object()
        for attr in ['description', 'description_teaser', 'ambiance', 'advice', 'access',
                     'public_transport', 'advised_parking', 'disabled_infrastructure']:
            setattr(trek, attr, plain_text(getattr(trek, attr)))
        context['object'] = trek
        context['trek'] = trek
        context['mapimage_ratio'] = trek.get_map_image_size()
        return context

    def render_to_response(self, context, **response_kwargs):
        trek = self.get_object()
        # Use attachment that overrides document print, if any.
        try:
            overriden = trek.get_attachment_print()
            response = HttpResponse(mimetype='application/vnd.oasis.opendocument.text')
            with open(overriden, 'rb') as f:
                response.write(f.read())
            return response
        except ObjectDoesNotExist:
            pass
        # Prepare altimetric graph
        trek.prepare_elevation_chart(self.request.build_absolute_uri('/'))
        return super(TrekDocumentPublic, self).render_to_response(context, **response_kwargs)


class TrekPrint(DocumentConvert):
    queryset = Trek.objects.existing()

    def source_url(self):
        return self.get_object().get_document_public_url()


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
    properties = ['name']


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
