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
                                MapEntityDetail, MapEntityDocument, MapEntityCreate, MapEntityUpdate, MapEntityDelete)
from caminae.mapentity.serializers import GPXSerializer
from caminae.common.views import json_django_dumps, HttpJSONResponse
from .models import Trek, POI, WebLink
from .filters import TrekFilter, POIFilter
from .forms import TrekForm, POIForm, WebLinkCreateFormPopup



class TrekLayer(MapEntityLayer):
    queryset = Trek.objects.existing()
    fields = ['name', 'departure', 'arrival', 'serializable_difficulty',
              'description', 'description_teaser', 'duration', 'ascent', 'descent', 
              'min_elevation', 'max_elevation', 'serializable_themes', 
              'serializable_usages', 'is_loop', 'published']


class TrekList(MapEntityList):
    queryset = Trek.objects.existing()
    filterform = TrekFilter
    columns = ['id', 'name', 'departure', 'arrival']


class TrekJsonList(MapEntityJsonList, TrekList):
    pass


class TrekFormatList(MapEntityFormat, TrekList):
    pass


class TrekJsonDetail(BaseDetailView):
    queryset = Trek.objects.existing()
    fields = ['name', 'departure', 'arrival', 'duration', 'description',
              'description_teaser', 'length', 'ascent', 'max_elevation',
              'advice', 'networks', 'ambiance', 'serializable_districts',
              'serializable_themes', 'serializable_usages',
              'serializable_cities', 'serializable_districts', 'access', 'ambiance',
              'serializable_weblinks', 'is_park_centered', 'disabled_infrastructure',
              'serializable_parking_location',]

    def get_context_data(self, **kwargs):
        o = self.object
        ctx = {}

        for fname in self.fields:
            prettyname = fname.replace('serializable_', '')
            ctx[prettyname] = getattr(o, fname)
            try:
                field = o._meta.get_field_by_name(fname)[0]
            except FieldDoesNotExist: # fname may refer to non-field properties
                pass
            else:
                if field in o._meta.many_to_many:
                    ctx[fname] = ctx[fname].all()

        return ctx

    def render_to_response(self, context):
        return HttpJSONResponse(json_django_dumps(context))


class TrekGPXDetail(BaseDetailView):
    queryset = Trek.objects.existing()

    def render_to_response(self, context):
        geom_field = 'geom'
        gpx_serializer = GPXSerializer()
        gpx_xml = gpx_serializer.serialize(self.get_queryset(), geom_field=geom_field)
        response = HttpResponse(gpx_xml, mimetype='application/gpx+xml')
        response['Content-Disposition'] = 'attachment; filename=trek-%s.gpx' % self.get_object().pk
        return response


class TrekKMLDetail(BaseDetailView):
    queryset = Trek.objects.existing()

    def render_to_response(self, context):
        trek = self.get_object()
        response = HttpResponse(trek.kml(), 
                                content_type = 'application/vnd.google-earth.kml+xml')
        return response


class TrekJsonProfile(BaseDetailView):
    queryset = Trek.objects.existing()

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        profile = self.object.elevation_profile
        return HttpJSONResponse(json_django_dumps({'profile': profile}))


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
    model = Trek

    def can_edit(self):
        return hasattr(self.request.user, 'profile') and \
               self.request.user.profile.is_trekking_manager()


class TrekDocument(MapEntityDocument):
    model = Trek


class TrekCreate(MapEntityCreate):
    model = Trek
    form_class = TrekForm

    @method_decorator(trekking_manager_required('trekking:trek_list'))
    def dispatch(self, *args, **kwargs):
        return super(TrekCreate, self).dispatch(*args, **kwargs)


class TrekUpdate(MapEntityUpdate):
    model = Trek
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
        pass


class POIDetail(MapEntityDetail):
    model = POI

    def can_edit(self):
        return hasattr(self.request.user, 'profile') and \
               self.request.user.profile.is_trekking_manager()


class POIDocument(MapEntityDocument):
    model = POI


class POICreate(MapEntityCreate):
    model = POI
    form_class = POIForm

    @method_decorator(trekking_manager_required('trekking:poi_list'))
    def dispatch(self, *args, **kwargs):
        return super(POICreate, self).dispatch(*args, **kwargs)


class POIUpdate(MapEntityUpdate):
    model = POI
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
        print form.instance
        return HttpResponse("""
            <script type="text/javascript">opener.dismissAddAnotherPopup(window, "%s", "%s");</script>
        """ % (escape(form.instance._get_pk_val()), escape(form.instance)))
