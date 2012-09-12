# -*- coding: utf-8 -*-
import csv

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import force_unicode
from django.utils.functional import Promise
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.views.decorators.http import last_modified as cache_last_modified
from django.core.cache import get_cache
from django.template.loader import find_template
from django.template.base import TemplateDoesNotExist

from shapes.views import ShpResponder
from djgeojson.views import GeoJSONLayerView
from djappypod.response import OdtTemplateResponse

from caminae.common.views import JSONResponseMixin  # TODO: mapentity should not have Caminae dependency

from . import models as mapentity_models
from .decorators import save_history


class MapEntityLayer(GeoJSONLayerView):
    """
    Take a class attribute `model` with a `latest_updated` method used for caching.
    """

    srid = settings.API_SRID

    def __init__(self, *args, **kwargs):
        super(GeoJSONLayerView, self).__init__(*args, **kwargs)
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
        super(ListView, self).__init__(*args, **kwargs)
        if self.model is None:
            self.model = self.queryset.model

    @classmethod
    def get_entity_kind(cls):
        return mapentity_models.ENTITY_LIST

    def get_queryset(self):
        qs = super(MapEntityList, self).get_queryset()
        return qs.select_related(depth=1)

    @method_decorator(login_required)
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
                columns.append(getattr(obj, field + '_display', getattr(obj, field)))
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

    @method_decorator(login_required)
    @save_history()
    def dispatch(self, *args, **kwargs):
        return super(MapEntityDetail, self).dispatch(*args, **kwargs)

    def can_edit(self):
        return False

    def get_context_data(self, **kwargs):
        context = super(MapEntityDetail, self).get_context_data(**kwargs)
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
        name_for = lambda app, object: "%s/%s%s.odt" % (app, object, self.template_name_suffix)
        try:
            template_name = name_for(self.model._meta.app_label, 
                                     self.model._meta.object_name.lower())
            # Try to access it!
            find_template(template_name)
            # If it exists, use it
            self.template_name = template_name
        except TemplateDoesNotExist:
            # It does not exist, use default one
            self.template_name = name_for("mapentity", "entity")

    def get_context_data(self, **kwargs):
        context = super(MapEntityDocument, self).get_context_data(**kwargs)
        # ODT template requires absolute URL for images insertion
        context['STATIC_URL'] = self.request.build_absolute_uri(settings.STATIC_URL)
        return context


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

    def __init__(self, *args, **kwargs):
        self.formats = {
            'csv': self.csv_view,
            'shp': self.shape_view,
        }
        super(MapEntityFormat, self).__init__(*args, **kwargs)

    @classmethod
    def get_entity_kind(cls):
        return mapentity_models.ENTITY_FORMAT_LIST

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        fmt_str = request.GET.get('format', 'csv')
        self.fmt = self.formats.get(fmt_str)

        if not self.fmt:
            raise Http404

        return super(MapEntityList, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """Get the right objects"""
        queryset = kwargs.pop('object_list')
        return { 'queryset': self.filterform(self.request.GET or None, queryset=queryset) }

    def render_to_response(self, context, **response_kwargs):
        """Delegate to the fmt view function found at dispatch time"""
        return self.fmt(
            request = self.request,
            context = context,
            **response_kwargs
        )

    def csv_view(self, request, context, **kwargs):
        def to_str(attr):
            if isinstance(attr, Promise):
                return force_unicode(attr)
            return str(attr)

        def get_lines():
            for obj in context['queryset']:
                columns = []
                for field in self.columns:
                    columns.append(to_str(
                        getattr(obj, field + '_display', getattr(obj, field))
                    ))
                yield columns

        response = HttpResponse(mimetype='text/csv')
        response['Content-Disposition'] = 'attachment; filename=list.csv'

        writer = csv.writer(response)
        writer.writerows(get_lines())

        return response

    def shape_view(self, request, context, **kwarg):
        queryset = context['queryset'].qs

        return MapEntityShpResponder(queryset,
            attribute_fieldnames=self.columns,
            geo_field='geom', # name of the geofield or None (if None, only one geofield should be presetn)
            proj_transform=settings.API_SRID, # proj_transform is for the output
            readme=None,
            file_name='shp_download',
            mimetype='application/zip',
        )()


class MapEntityShpResponder(ShpResponder):
    def __init__(self, *args, **kwargs):
        self.attribute_fieldnames = kwargs.pop('attribute_fieldnames', None)
        super(MapEntityShpResponder, self).__init__(*args, **kwargs)

    def get_attributes(self):
        attrs = super(MapEntityShpResponder, self).get_attributes()
        if self.attribute_fieldnames is not None:
            attrs = [ f for f in attrs if attrs in self.attribute_fieldnames ]
        return attrs
