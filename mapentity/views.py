# -*- coding: utf-8 -*-
import urllib2
import logging
from datetime import datetime

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db.models.query import QuerySet
from django.http import HttpResponse, HttpResponseBadRequest
from django.utils.translation import ugettext_lazy as _
from django.utils import simplejson
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from django.utils.decorators import method_decorator
from django.utils.encoding import force_unicode
from django.utils.functional import Promise, curry
from django.contrib import messages
from django.views.decorators.http import require_http_methods, last_modified as cache_last_modified
from django.views.decorators.csrf import csrf_exempt
from django.core.serializers import serialize
from django.core.serializers.json import DateTimeAwareJSONEncoder
from django.core.cache import get_cache
from django.template.base import TemplateDoesNotExist

from djgeojson.views import GeoJSONLayerView
from djappypod.odt import get_template
from djappypod.response import OdtTemplateResponse
from screamshot.decorators import login_required_capturable
from screamshot.utils import casperjs_capture

from . import models as mapentity_models
from .decorators import save_history
from .serializers import GPXSerializer, CSVSerializer, DatatablesSerializer, ZipShapeSerializer

logger = logging.getLogger(__name__)


"""

    Reusables

"""
class HttpJSONResponse(HttpResponse):
    def __init__(self, content='', **kwargs):
        kwargs['content_type'] = 'application/json'
        super(HttpJSONResponse, self).__init__(content, **kwargs)


class DjangoJSONEncoder(DateTimeAwareJSONEncoder):
    """
    Taken (slightly modified) from:
    http://stackoverflow.com/questions/2249792/json-serializing-django-models-with-simplejson
    """
    def default(self, obj):
        # https://docs.djangoproject.com/en/dev/topics/serialization/#id2
        if isinstance(obj, Promise):
            return force_unicode(obj)
        if isinstance(obj, QuerySet):
            # `default` must return a python serializable
            # structure, the easiest way is to load the JSON
            # string produced by `serialize` and return it
            return simplejson.loads(serialize('json', obj))
        return super(DjangoJSONEncoder, self).default(obj)

# partial function, we can now use dumps(my_dict) instead
# of dumps(my_dict, cls=DjangoJSONEncoder)
json_django_dumps = curry(simplejson.dumps, cls=DjangoJSONEncoder)


class JSONResponseMixin(object):
    """
    A mixin that can be used to render a JSON response.
    """
    response_class = HttpJSONResponse

    def render_to_response(self, context, **response_kwargs):
        """
        Returns a JSON response, transforming 'context' to make the payload.
        """
        return self.response_class(
            self.convert_context_to_json(context),
            **response_kwargs
        )

    def convert_context_to_json(self, context):
        "Convert the context dictionary into a JSON object"
        return json_django_dumps(context)


"""

    Concrete views

"""
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


@require_http_methods(["POST"])
@csrf_exempt
@login_required
def history_delete(request, path=None):
    path = request.POST.get('path', path)
    if path:
        history = request.session['history']
        history = [h for h in history if h.path != path]
        request.session['history'] = history
    return HttpResponse()




"""

    Generic views

"""

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
        key = '%s_%s_layer_json' % (self.request.LANGUAGE_CODE,
                                    self.model._meta.module_name)

        result = cache.get(key)
        latest = self.model.latest_updated()

        if result and latest:
            cache_latest, content = result
            # Not empty and still valid
            if cache_latest and cache_latest >= latest:
                return self.response_class(content=content, **response_kwargs)

        response = super(MapEntityLayer, self).render_to_response(context, **response_kwargs)
        cache.set(key, (latest, response.content))
        return response


class ModelMetaMixin(object):
    """
    Add model meta information in context data 
    """

    def get_entity_kind(self):
        return None

    def get_title(self):
        return None

    def get_context_data(self, **kwargs):
        context = super(ModelMetaMixin, self).get_context_data(**kwargs)
        context['view'] = self.get_entity_kind()
        context['title'] = self.get_title()

        model = self.model or self.queryset.model
        if model:
            context['model'] = model
            context['appname'] = model._meta.app_label.lower()
            context['modelname'] = model._meta.object_name.lower()
            context['objectsname'] = model._meta.verbose_name_plural
        return context


class MapEntityList(ModelMetaMixin, ListView):
    """
    
    A generic view list web page.
    
    """
    model = None
    filterform = None
    columns = []

    def __init__(self, *args, **kwargs):
        super(MapEntityList, self).__init__(*args, **kwargs)
        self._filterform = None
        if self.model is None:
            self.model = self.queryset.model

    @classmethod
    def get_entity_kind(cls):
        return mapentity_models.ENTITY_LIST

    def get_queryset(self):
        queryset = super(MapEntityList, self).get_queryset()
        queryset = queryset.select_related(depth=1)
        # Filter queryset from possible serialized form
        self._filterform = self.filterform(self.request.GET or None, queryset=queryset)
        return self._filterform.qs

    @method_decorator(login_required_capturable)
    def dispatch(self, request, *args, **kwargs):
        # Save last list visited in session
        request.session['last_list'] = request.path
        return super(MapEntityList, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(MapEntityList, self).get_context_data(**kwargs)
        context['datatables_ajax_url'] = self.model.get_jsonlist_url()
        context['filterform'] = self._filterform
        context['columns'] = self.columns
        context['generic_detail_url'] = self.model.get_generic_detail_url()
        return context


class MapEntityJsonList(JSONResponseMixin, MapEntityList):
    """
    Return path related datas (belonging to the current user) as a JSON
    that will populate a dataTable.
    """

    @classmethod
    def get_entity_kind(cls):
        return mapentity_models.ENTITY_JSON_LIST

    def dispatch(self, *args, **kwargs):
        return super(ListView, self).dispatch(*args, **kwargs)  # Bypass login_required

    def get_context_data(self, **kwargs):
        """
        Override the most important part of JSONListView... (paginator)
        """
        serializer = DatatablesSerializer()
        return serializer.serialize(self.get_queryset(), fields=self.columns)


class MapEntityFormat(MapEntityList):
    """Make it  extends your EntityList"""
    DEFAULT_FORMAT = 'csv'

    @classmethod
    def get_entity_kind(cls):
        return mapentity_models.ENTITY_FORMAT_LIST

    def get_context_data(self, **kwargs):
        return {}

    def render_to_response(self, context, **response_kwargs):
        """Delegate to the fmt view function found at dispatch time"""
        formats = {
            'csv': self.csv_view,
            'shp': self.shape_view,
            'gpx': self.gpx_view,
        }
        fmt_str = self.request.GET.get('format', self.DEFAULT_FORMAT)
        formatter = formats.get(fmt_str)
        if not formatter:
            logger.warning("Unknown serialization format '%s'" % fmt_str)
            return HttpResponseBadRequest()

        return formatter(request = self.request, context = context, **response_kwargs)

    def csv_view(self, request, context, **kwargs):
        serializer = CSVSerializer()
        response = HttpResponse(mimetype='text/csv')
        response['Content-Disposition'] = 'attachment; filename=list.csv'
        serializer.serialize(queryset=self.get_queryset(), stream=response, 
                             fields=self.columns, ensure_ascii=True)
        return response

    def shape_view(self, request, context, **kwargs):
        serializer = ZipShapeSerializer()
        response = HttpResponse(mimetype='application/zip')
        response['Content-Disposition'] = 'attachment; filename=list.zip'
        serializer.serialize(queryset=self.get_queryset(), stream=response, 
                             fields=self.columns)
        response['Content-length'] = str(len(response.content))
        return response

    def gpx_view(self, request, context, **kwargs):
        serializer = GPXSerializer()
        response = HttpResponse(mimetype='application/gpx+xml')
        response['Content-Disposition'] = 'attachment; filename=list.gpx'
        serializer.serialize(self.get_queryset(), stream=response, geom_field='geom')
        return response


class MapEntityDetail(ModelMetaMixin, DetailView):
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


class MapEntityCreate(ModelMetaMixin, CreateView):
    @classmethod
    def get_entity_kind(cls):
        return mapentity_models.ENTITY_CREATE

    @classmethod
    def get_title(cls):
        name = cls.model._meta.verbose_name
        if hasattr(name, '_proxy____args'):
            name = name._proxy____args[0]  # untranslated
        # Whole "add" phrase translatable, but not catched  by makemessages
        return _(u"Add a new %s" % name.lower())

    @method_decorator(login_required)
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
        return context


class MapEntityUpdate(ModelMetaMixin, UpdateView):
    @classmethod
    def get_entity_kind(cls):
        return mapentity_models.ENTITY_UPDATE

    def get_title(self):
        return _("Edit %s") % self.get_object()

    @method_decorator(login_required)
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
        context['can_delete_attachment'] = True   # Consider that if can edit, then can delete
        return context


class MapEntityDelete(DeleteView):
    @classmethod
    def get_entity_kind(cls):
        return mapentity_models.ENTITY_DELETE

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(MapEntityDelete, self).dispatch(*args, **kwargs)

    def delete(self, request, *args, **kwargs):
        # Remove entry from history
        history_delete(request, path=self.get_object().get_detail_url())
        return super(MapEntityDelete, self).delete(request, *args, **kwargs)

    def get_success_url(self):
        return self.model.get_list_url()
