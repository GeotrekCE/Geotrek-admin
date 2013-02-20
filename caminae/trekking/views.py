from django.conf import settings
from django.http import HttpResponse, Http404
from django.db.models.fields import FieldDoesNotExist
from django.utils.decorators import method_decorator
from django.utils.html import escape
from django.views.generic.edit import CreateView
from django.views.generic.detail import BaseDetailView

from djgeojson.views import GeoJSONLayerView

from caminae.authent.decorators import trekking_manager_required
from caminae.mapentity.views import (MapEntityLayer, MapEntityList, MapEntityJsonList, MapEntityFormat,
                                     MapEntityDetail, MapEntityDocument, MapEntityCreate, MapEntityUpdate, MapEntityDelete,
                                     JSONResponseMixin)
from caminae.mapentity.serializers import GPXSerializer
from caminae.common.views import FormsetMixin
from .models import Trek, POI, WebLink
from .filters import TrekFilter, POIFilter
from .forms import TrekForm, TrekRelationshipFormSet, POIForm, WebLinkCreateFormPopup


class TrekLayer(MapEntityLayer):
    queryset = Trek.objects.existing()
    fields = ['arrival', 'ascent', 'departure', 'descent', 'description', 'description_teaser', 
              'duration', 'is_loop', 'max_elevation', 'min_elevation', 'name', 'published', 
              'serializable_difficulty', 'serializable_themes', 'serializable_usages']


class TrekList(MapEntityList):
    queryset = Trek.objects.existing()
    filterform = TrekFilter
    columns = ['id', 'name', 'duration', 'difficulty', 'departure', 'arrival']


class TrekJsonList(MapEntityJsonList, TrekList):
    pass


class TrekJsonDetail(JSONResponseMixin, BaseDetailView):
    queryset = Trek.objects.existing()
    columns = ['name', 'departure', 'arrival', 'duration', 'description',
              'description_teaser', 'length', 'ascent', 'descent', 
              'max_elevation', 'min_elevation', 'published',
              'advice', 'networks', 'ambiance', 'difficulty',
              'themes', 'usages', 'access', 'route',
              'web_links', 'is_park_centered', 'disabled_infrastructure',
              'parking_location', 'picture',
              'cities', 'districts']

    def get_context_data(self, **kwargs):
        o = self.object
        ctx = {}

        for fname in self.columns:
            ctx[fname] = getattr(o, 'serializable_%s' % fname, getattr(o, fname))
            try:
                field = o._meta.get_field_by_name(fname)[0]
            except FieldDoesNotExist: # fname may refer to non-field properties
                pass
            else:
                if field in o._meta.many_to_many:
                    ctx[fname] = getattr(o, fname).all()

        return ctx


class TrekFormatList(MapEntityFormat, TrekList):
    columns = set(TrekList.columns + TrekJsonDetail.columns + ['pois']) - set(['picture',])


class TrekGPXDetail(BaseDetailView):
    queryset = Trek.objects.existing()

    def render_to_response(self, context):
        gpx_serializer = GPXSerializer()
        response = HttpResponse(mimetype='application/gpx+xml')
        response['Content-Disposition'] = 'attachment; filename=trek-%s.gpx' % self.get_object().pk
        gpx_serializer.serialize(self.get_queryset(), stream=response, geom_field='geom')
        return response


class TrekKMLDetail(BaseDetailView):
    queryset = Trek.objects.existing()

    def render_to_response(self, context):
        trek = self.get_object()
        response = HttpResponse(trek.kml(), 
                                content_type = 'application/vnd.google-earth.kml+xml')
        return response


class TrekJsonProfile(JSONResponseMixin, BaseDetailView):
    queryset = Trek.objects.existing()

    def get_context_data(self, **kwargs):
        t = self.get_object()
        return {'profile': t.elevation_profile}


class TrekPOIGeoJSON(GeoJSONLayerView):
    srid = settings.API_SRID
    pk_url_kwarg = 'pk'
    fields = ['name', 'description', 'serializable_type']

    def get_queryset(self):
        try:
            trek_pk = self.kwargs.get(self.pk_url_kwarg)
            trek = Trek.objects.get(pk=trek_pk)
        except Trek.DoesNotExist:
            raise Http404
        return trek.pois.select_related(depth=1)


class TrekDetail(MapEntityDetail):
    queryset = Trek.objects.existing()

    def can_edit(self):
        return self.request.user.is_staff or \
               (hasattr(self.request.user, 'profile') and \
                self.request.user.profile.is_trekking_manager())


class TrekDocument(MapEntityDocument):
    model = Trek


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
    columns = ['id', 'name', 'type']


class POIJsonList(MapEntityJsonList, POIList):
    pass


class POIFormatList(MapEntityFormat, POIList):
    columns = set(POIList.columns + ['description', 'treks', 'districts', 'cities', 'areas'])


class POIDetail(MapEntityDetail):
    queryset = POI.objects.existing()

    def can_edit(self):
        return self.request.user.is_staff or \
               (hasattr(self.request.user, 'profile') and \
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
