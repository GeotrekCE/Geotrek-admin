# -*- coding: utf-8 -*-
import csv
import math
import urllib2
import logging
from datetime import datetime

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404, HttpResponseBadRequest
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import smart_str
from django.utils import simplejson
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.views.decorators.http import last_modified as cache_last_modified
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import get_cache
from django.template.base import TemplateDoesNotExist
from django.contrib.gis.db.models.fields import (
        GeometryField, GeometryCollectionField, PointField, LineStringField
)

from djgeojson.views import GeoJSONLayerView
from djappypod.odt import get_template
from djappypod.response import OdtTemplateResponse
from screamshot.decorators import login_required_capturable
from screamshot.utils import casperjs_capture

from caminae.common.views import JSONResponseMixin  # TODO: mapentity should not have Caminae dependency
from caminae.core.models import split_bygeom # TODO

from . import models as mapentity_models
from . import shape_exporter
from .decorators import save_history
from .serializers import GPXSerializer

logger = logging.getLogger(__name__)

# Concrete views

@csrf_exempt
@login_required
def map_screenshot(request):
    """
    This view allows to take screenshots, via django-screamshot, of
    the map currently viewed by the user.
    
    - A context full of information is built on client-side and posted here.
    - We reproduce this context, via headless browser, and take a capture
    - We return the resulting image as attachment.
    
    This seems overkill ? Please look around and find a better way.
    """
    try:
        printcontext = request.POST['printcontext']
        assert len(printcontext) < 512, "Print context is way too big."
        
        # Prepare context, extract and add infos
        context = simplejson.loads(printcontext.encode("utf-8"))
        map_url = context.pop('url').split('?', 1)[0]
        context['print'] = True
        printcontext = simplejson.dumps(context)
        logger.debug("Print context received : %s" % printcontext)

        # Provide print context to destination
        printcontext = str(printcontext.encode('latin-1'))  # TODO this is wrong
        contextencoded = urllib2.quote(printcontext)
        map_url += '?context=%s' % contextencoded
        # Capture image and return it
        width = context.get('viewport', {}).get('width')
        height = context.get('viewport', {}).get('height')
        response = HttpResponse(mimetype='image/png')
        response['Content-Disposition'] = 'attachment; filename=%s.png' % datetime.now().strftime('%Y%m%d-%H%M%S')
        casperjs_capture(response, map_url, width=width, height=height, selector='#mainmap')
        return response

    except Exception, e: 
        logger.exception(e)
        return HttpResponseBadRequest(e)


# Generic views, to be overriden

class MapEntityLayer(GeoJSONLayerView):
    """
    Take a class attribute `model` with a `latest_updated` method used for caching.
    """

    srid = settings.API_SRID

    def __init__(self, *args, **kwargs):
        super(MapEntityLayer, self).__init__(*args, **kwargs)
        if self.model is None:
            self.model = self.queryset.model

    @classmethod
    def get_entity_kind(cls):
        return mapentity_models.ENTITY_LAYER

    def dispatch(self, *args, **kwargs):
        # Use lambda to bound self and to avoid passing request, *args, **kwargs as the decorator would do
        # TODO: we should be storing cache_latest and cache_latest_dispatch for reuse
        # but it triggers other problems (self.cache_latest() - will pass self as an unwanted arg)
        cache_latest = cache_last_modified(lambda x: self.model.latest_updated())
        cache_latest_dispatch = cache_latest(super(MapEntityLayer, self).dispatch)
        return cache_latest_dispatch(*args, **kwargs)

    def render_to_response(self, context, **response_kwargs):
        cache = get_cache('fat')
        key = '%s_layer_json' % self.model._meta.module_name

        result = cache.get(key)
        latest = self.model.latest_updated()

        if result and latest:
            cache_latest, content = result
            # still valid
            if cache_latest >= latest:
                return self.response_class(content=content, **response_kwargs)

        response = super(MapEntityLayer, self).render_to_response(context, **response_kwargs)
        cache.set(key, (latest, response.content))
        return response


class MapEntityList(ListView):
    """
    
    A generic view list web page.
    
    model = None
    filterform = None
    columns = []
    """

    def __init__(self, *args, **kwargs):
        super(MapEntityList, self).__init__(*args, **kwargs)
        if self.model is None:
            self.model = self.queryset.model

    @classmethod
    def get_entity_kind(cls):
        return mapentity_models.ENTITY_LIST

    def get_queryset(self):
        qs = super(MapEntityList, self).get_queryset()
        return qs.select_related(depth=1)

    @method_decorator(login_required_capturable)
    def dispatch(self, request, *args, **kwargs):
        # Save last list visited in session
        request.session['last_list'] = request.path
        return super(MapEntityList, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(MapEntityList, self).get_context_data(**kwargs)
        context.update(**dict(
            model=self.model,
            objectsname=self.model._meta.verbose_name_plural,
            datatables_ajax_url=self.model.get_jsonlist_url(),
            filterform=self.filterform(None, queryset=self.get_queryset()),
            columns=self.columns,
            generic_detail_url=self.model.get_generic_detail_url(),
        ))
        return context


class MapEntityJsonList(JSONResponseMixin, MapEntityList):
    """
    Return path related datas (belonging to the current user) as a JSON
    that will populate a dataTable.

    TODO: provide filters, pagination, sorting etc.
          At the moment everything (except the first listing) is done client side
    """
    # aaData is the key looked up by dataTables
    data_table_name = 'aaData'

    @classmethod
    def get_entity_kind(cls):
        return mapentity_models.ENTITY_JSON_LIST

    def dispatch(self, *args, **kwargs):
        return super(ListView, self).dispatch(*args, **kwargs)  # Bypass login_required

    def get_context_data(self, **kwargs):
        """
        override the most important part of JSONListView... (paginator)
        """
        queryset = kwargs.pop('object_list')
        # Filter queryset from possible serialized form
        queryset = self.filterform(self.request.GET or None, queryset=queryset)
        # Build list with fields
        map_obj_pk = []
        data_table_rows = []
        for obj in queryset:
            columns = []
            for field in self.columns:
                value = getattr(obj, field + '_display', getattr(obj, field))
                if isinstance(value, float) and math.isnan(value): value = 0.0
                columns.append(value)
            data_table_rows.append(columns)
            map_obj_pk.append(obj.pk)

        context = {
            self.data_table_name: data_table_rows,
            'map_obj_pk': map_obj_pk,
        }
        return context


class MapEntityDetail(DetailView):
    @classmethod
    def get_entity_kind(cls):
        return mapentity_models.ENTITY_DETAIL

    def get_title(self):
        return unicode(self.get_object())

    @method_decorator(login_required_capturable)
    @save_history()
    def dispatch(self, *args, **kwargs):
        return super(MapEntityDetail, self).dispatch(*args, **kwargs)

    def can_edit(self):
        return False

    def get_context_data(self, **kwargs):
        context = super(MapEntityDetail, self).get_context_data(**kwargs)
        context['modelname'] = self.model._meta.object_name.lower()
        context['can_edit'] = self.can_edit()
        context['can_delete_attachment'] = self.can_edit()
        return context


class MapEntityDocument(DetailView):
    response_class = OdtTemplateResponse

    @classmethod
    def get_entity_kind(cls):
        return mapentity_models.ENTITY_DOCUMENT

    def __init__(self, *args, **kwargs):
        super(MapEntityDocument, self).__init__(*args, **kwargs)
        # Try to load template for each lang and object detail
        name_for = lambda app, object, lang: "%s/%s%s%s.odt" % (app, object, lang, self.template_name_suffix)
        langs = ['_%s' % lang for lang, langname in settings.LANGUAGES]
        langs.append('')   # Will also try without lang
        found = None
        for lang in langs:
            try:
                template_name = name_for(self.model._meta.app_label, 
                                         self.model._meta.object_name.lower(),
                                         lang)
                get_template(template_name)
                found = template_name
                break
            except TemplateDoesNotExist:
                pass
        if not found:
            for lang in langs:
                try:
                    template_name = name_for("mapentity", "entity", lang) 
                    get_template(template_name)
                    found = template_name
                    break
                except TemplateDoesNotExist:
                    pass
        if not found:
            raise TemplateDoesNotExist(name_for(self.model._meta.app_label, self.model._meta.object_name.lower(), ''))
        self.template_name = found

    def get_context_data(self, **kwargs):
        context = super(MapEntityDocument, self).get_context_data(**kwargs)
        # ODT template requires absolute URL for images insertion
        context['datetime'] = datetime.now()
        context['STATIC_URL'] = self.request.build_absolute_uri(settings.STATIC_URL)[:-1]
        context['MEDIA_URL'] = self.request.build_absolute_uri(settings.MEDIA_URL)[:-1]
        context['MEDIA_ROOT'] = settings.MEDIA_ROOT
        return context

    def dispatch(self, *args, **kwargs):
        handler = super(MapEntityDocument, self).dispatch(*args, **kwargs)
        # Screenshot of object map
        self.get_object().prepare_map_image(self.request.build_absolute_uri(settings.ROOT_URL or '/'))
        return handler


class MapEntityCreate(CreateView):
    @classmethod
    def get_entity_kind(cls):
        return mapentity_models.ENTITY_CREATE

    @classmethod
    def get_title(cls):
        name = cls.model._meta.verbose_name
        if hasattr(name, '_proxy____args'):
            name = name._proxy____args[0]  # untranslated
        # Whole "add" phrase translatable, but not catched  by makemessages
        return _("Add a new %s" % name.lower())

    @method_decorator(login_required)
    @save_history()
    def dispatch(self, *args, **kwargs):
        return super(MapEntityCreate, self).dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(MapEntityCreate, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, _("Created"))
        return super(MapEntityCreate, self).form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, _("Your form contains errors"))
        return super(MapEntityCreate, self).form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super(MapEntityCreate, self).get_context_data(**kwargs)
        context['modelname'] = self.model._meta.object_name.lower()
        context['title'] = self.get_title()
        return context


class MapEntityUpdate(UpdateView):
    @classmethod
    def get_entity_kind(cls):
        return mapentity_models.ENTITY_UPDATE

    def get_title(self):
        return _("Edit %s") % self.get_object()

    @method_decorator(login_required)
    @save_history()
    def dispatch(self, *args, **kwargs):
        return super(MapEntityUpdate, self).dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(MapEntityUpdate, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, _("Saved"))
        return super(MapEntityUpdate, self).form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, _("Your form contains errors"))
        return super(MapEntityUpdate, self).form_invalid(form)

    def get_success_url(self):
        return self.get_object().get_detail_url()

    def get_context_data(self, **kwargs):
        context = super(MapEntityUpdate, self).get_context_data(**kwargs)
        context['modelname'] = self.model._meta.object_name.lower()
        context['title'] = self.get_title()
        context['can_delete_attachment'] = True   # Consider that if can edit, then can delete
        return context


class MapEntityDelete(DeleteView):
    @classmethod
    def get_entity_kind(cls):
        return mapentity_models.ENTITY_DELETE

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(MapEntityDelete, self).dispatch(*args, **kwargs)

    def get_success_url(self):
        return self.model.get_list_url()


class MapEntityFormat(MapEntityList):
    """Make it  extends your EntityList"""
    DEFAULT_FORMAT = 'csv'

    def __init__(self, *args, **kwargs):
        self.formats = {
            'csv': self.csv_view,
            'shp': self.shape_view,
            'gpx': self.gpx_view,
        }
        super(MapEntityFormat, self).__init__(*args, **kwargs)

    @classmethod
    def get_entity_kind(cls):
        return mapentity_models.ENTITY_FORMAT_LIST

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        fmt_str = request.GET.get('format', self.DEFAULT_FORMAT)
        self.formatter = self.formats.get(fmt_str)

        if not self.formatter:
            logger.warning(_("Unknown serialization format '%s'") % fmt_str)
            raise Http404

        return super(MapEntityList, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """Get the right objects"""
        queryset = kwargs.pop('object_list')
        return { 'queryset': self.filterform(self.request.GET or None, queryset=queryset) }

    def render_to_response(self, context, **response_kwargs):
        """Delegate to the fmt view function found at dispatch time"""
        return self.formatter(
            request = self.request,
            context = context,
            **response_kwargs
        )

    def csv_view(self, request, context, **kwargs):
        """
        Uses self.columns, containing fieldnames to produce the CSV.
        The header of the csv is made of the verbose name of each field
        Each column content is made using (by priority order):
            * <field_name>_csv_display
            * <field_name>_display
            * <field_name>
        """

        def get_lines():
            queryset = context['queryset'].qs

            # Header line
            yield [
                smart_str(queryset.model._meta.get_field(field).verbose_name)
                for field in self.columns
            ]

            for obj in queryset:
                columns = []
                for field in self.columns:
                    # may be optimized
                    columns.append(smart_str(
                        getattr(obj, field + '_csv_display',
                            getattr(obj, field + '_display',
                                getattr(obj, field)
                            )
                        )
                    ))
                yield columns

        response = HttpResponse(mimetype='text/csv')
        response['Content-Disposition'] = 'attachment; filename=list.csv'

        writer = csv.writer(response)
        writer.writerows(get_lines())

        return response

    def shape_view(self, request, context, **kwarg):
        queryset = context['queryset'].qs

        shp_creator = shape_exporter.ShapeCreator()

        self.create_shape(shp_creator, queryset)

        return shp_creator.as_zipped_response('shp_download')

    def create_shape(self, shp_creator, queryset):
        """Split a shapes into one or more shapes (one for point and one for linestring)"""
        fieldmap = self.get_fieldmap(queryset)
        # Don't use this - projection does not work yet (looses z dimension)
        # srid_out = settings.API_SRID

        get_geom, geom_type, srid = self.get_geom_info(queryset.model)

        if geom_type in (GeometryField.geom_type, GeometryCollectionField.geom_type):
            by_points, by_linestrings = self.split_points_linestrings(queryset, get_geom)

            for split_qs, split_geom_field in ((by_points, PointField), (by_linestrings, LineStringField)):
                split_geom_type = split_geom_field.geom_type

                shp_filepath = shape_exporter.shape_write(
                                    split_qs, fieldmap, get_geom, split_geom_type, srid)

                shp_creator.add_shape('shp_download_%s' % split_geom_type.lower(), shp_filepath)
        else:
            shp_filepath = shape_exporter.shape_write(
                                queryset, fieldmap, get_geom, geom_type, srid)

            shp_creator.add_shape('shp_download', shp_filepath)

    def split_points_linestrings(self, queryset, get_geom):
        return split_bygeom(queryset, geom_getter=get_geom)

    def get_fieldmap(self, qs):
        return shape_exporter.fieldmap_from_fields(qs.model, self.columns)

    def get_geom_info(self, model):
        geo_field = shape_exporter.geo_field_from_model(model, 'geom')
        get_geom, geom_type, srid = shape_exporter.info_from_geo_field(geo_field)
        return get_geom, geom_type, srid

    def gpx_view(self, request, context, **kwargs):
        queryset = context['queryset'].qs
        geom_field = 'geom'
        gpx_serializer = GPXSerializer()
        # Can't use values_list('geom', flat=True) as some geom are not a field but a property
        qs = queryset.select_related(depth=1)
        gpx_xml = gpx_serializer.serialize(qs, geom_field=geom_field)
        
        response = HttpResponse(gpx_xml, mimetype='application/gpx+xml')
        response['Content-Disposition'] = 'attachment; filename=list.gpx'
        return response
