import os

from django.conf import settings
from django.http import HttpResponse, Http404
from django.utils.decorators import method_decorator
from django.utils.html import escape
from django.views.generic.edit import CreateView
from django.views.generic.detail import BaseDetailView

from djgeojson.views import GeoJSONLayerView

from caminae.authent.decorators import trekking_manager_required
from caminae.mapentity.views import (MapEntityLayer, MapEntityList, MapEntityJsonList, MapEntityFormat,
                                     MapEntityDetail, MapEntityDocument, MapEntityCreate, MapEntityUpdate, MapEntityDelete,
                                     LastModifiedMixin, JSONResponseMixin)
from caminae.mapentity.serializers import GPXSerializer
from caminae.common.views import FormsetMixin
from .models import Trek, POI, WebLink
from .filters import TrekFilter, POIFilter
from .forms import TrekForm, TrekRelationshipFormSet, POIForm, WebLinkCreateFormPopup


class TrekLayer(MapEntityLayer):
    fields = ['name', 'published']
    queryset = Trek.objects.existing()


class TrekList(MapEntityList):
    queryset = Trek.objects.existing()
    filterform = TrekFilter
    columns = ['id', 'name', 'duration', 'difficulty', 'departure', 'thumbnail']


class TrekJsonList(MapEntityJsonList, TrekList):
    pass


class TrekJsonDetail(LastModifiedMixin, JSONResponseMixin, BaseDetailView):
    queryset = Trek.objects.existing()
    columns = ['name', 'slug', 'departure', 'arrival', 'duration', 'description',
               'description_teaser', 'length', 'ascent', 'descent',
               'max_elevation', 'min_elevation', 'published',
               'networks', 'advice', 'ambiance', 'difficulty',
               'themes', 'usages', 'access', 'route',
               'web_links', 'is_park_centered', 'disabled_infrastructure',
               'parking_location', 'thumbnail', 'pictures',
               'cities', 'districts', 'relationships', 'map_image_url']

    def dispatch(self, *args, **kwargs):
        handler = BaseDetailView.dispatch(self, *args, **kwargs)
        # Screenshot of object map
        self.get_object().prepare_map_image(self.request.build_absolute_uri(settings.ROOT_URL or '/'))
        return handler

    def get_context_data(self, **kwargs):
        ctx = {}
        for fname in self.columns:
            ctx[fname] = getattr(self.object, 'serializable_%s' % fname,
                                 getattr(self.object, fname))
        return ctx


class TrekFormatList(MapEntityFormat, TrekList):
    columns = set(TrekList.columns + TrekJsonDetail.columns + ['related', 'pois']) - set(['relationships', 'thumbnail'])


class TrekGPXDetail(LastModifiedMixin, BaseDetailView):
    queryset = Trek.objects.existing()

    def render_to_response(self, context):
        gpx_serializer = GPXSerializer()
        response = HttpResponse(mimetype='application/gpx+xml')
        response['Content-Disposition'] = 'attachment; filename=trek-%s.gpx' % self.get_object().pk
        gpx_serializer.serialize(self.get_queryset(), stream=response, geom_field='geom')
        return response


class TrekKMLDetail(LastModifiedMixin, BaseDetailView):
    queryset = Trek.objects.existing()

    def render_to_response(self, context):
        trek = self.get_object()
        response = HttpResponse(trek.kml(),
                                content_type='application/vnd.google-earth.kml+xml')
        return response


class TrekJsonProfile(LastModifiedMixin, JSONResponseMixin, BaseDetailView):
    queryset = Trek.objects.existing()

    def get_context_data(self, **kwargs):
        t = self.get_object()
        return {'profile': t.elevation_profile}


class TrekPOIGeoJSON(LastModifiedMixin, GeoJSONLayerView):
    model = Trek  # for LastModifiedMixin
    srid = settings.API_SRID
    pk_url_kwarg = 'pk'
    fields = ['name', 'description', 'serializable_thumbnail', 'serializable_type', 'serializable_pictures']

    def get_queryset(self):
        try:
            trek_pk = self.kwargs.get(self.pk_url_kwarg)
            trek = Trek.objects.get(pk=trek_pk)
        except Trek.DoesNotExist:
            raise Http404
        # All POIs of this trek
        return trek.pois.select_related(depth=1)


class TrekDetail(MapEntityDetail):
    queryset = Trek.objects.existing()

    def can_edit(self):
        return self.request.user.is_staff or (
            hasattr(self.request.user, 'profile') and
            self.request.user.profile.is_trekking_manager())


class TrekDocument(MapEntityDocument):
    model = Trek


class TrekDocumentPublic(TrekDocument):
    template_name_suffix = "_public"


class TrekDocumentPublicPOI(TrekDocumentPublic):
    template_name_suffix = "_public_poi"


class TrekRelationshipFormsetMixin(FormsetMixin):
    context_name = 'relationship_formset'
    formset_class = TrekRelationshipFormSet


class TrekCreate(TrekRelationshipFormsetMixin, MapEntityCreate):
    model = Trek
    form_class = TrekForm

    @method_decorator(trekking_manager_required('trekking:trek_list'))
    def dispatch(self, *args, **kwargs):
        return super(TrekCreate, self).dispatch(*args, **kwargs)


class TrekUpdate(TrekRelationshipFormsetMixin, MapEntityUpdate):
    queryset = Trek.objects.existing()
    form_class = TrekForm

    @method_decorator(trekking_manager_required('trekking:trek_detail'))
    def dispatch(self, *args, **kwargs):
        return super(TrekUpdate, self).dispatch(*args, **kwargs)


class TrekDelete(MapEntityDelete):
    model = Trek

    @method_decorator(trekking_manager_required('trekking:trek_detail'))
    def dispatch(self, *args, **kwargs):
        return super(TrekDelete, self).dispatch(*args, **kwargs)


class POILayer(MapEntityLayer):
    queryset = POI.objects.existing()


class POIList(MapEntityList):
    queryset = POI.objects.existing()
    filterform = POIFilter
    columns = ['id', 'name', 'type', 'thumbnail']


class POIJsonList(MapEntityJsonList, POIList):
    pass


class POIFormatList(MapEntityFormat, POIList):
    columns = set(POIList.columns + ['description', 'treks', 'districts', 'cities', 'areas'])


class POIDetail(MapEntityDetail):
    queryset = POI.objects.existing()

    def can_edit(self):
        return self.request.user.is_staff or (
            hasattr(self.request.user, 'profile') and
            self.request.user.profile.is_trekking_manager())


class POIDocument(MapEntityDocument):
    model = POI


class POICreate(MapEntityCreate):
    model = POI
    form_class = POIForm

    @method_decorator(trekking_manager_required('trekking:poi_list'))
    def dispatch(self, *args, **kwargs):
        return super(POICreate, self).dispatch(*args, **kwargs)


class POIUpdate(MapEntityUpdate):
    queryset = POI.objects.existing()
    form_class = POIForm

    @method_decorator(trekking_manager_required('trekking:poi_detail'))
    def dispatch(self, *args, **kwargs):
        return super(POIUpdate, self).dispatch(*args, **kwargs)


class POIDelete(MapEntityDelete):
    model = POI

    @method_decorator(trekking_manager_required('trekking:poi_detail'))
    def dispatch(self, *args, **kwargs):
        return super(POIDelete, self).dispatch(*args, **kwargs)


class WebLinkCreatePopup(CreateView):
    model = WebLink
    form_class = WebLinkCreateFormPopup

    def form_valid(self, form):
        self.object = form.save()
        return HttpResponse("""
            <script type="text/javascript">opener.dismissAddAnotherPopup(window, "%s", "%s");</script>
        """ % (escape(form.instance._get_pk_val()), escape(form.instance)))
