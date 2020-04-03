import logging

from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.gis.db.models import GeometryField
from django.http import HttpResponse, HttpResponseNotFound
from django.views.decorators.http import last_modified as cache_last_modified

from ..registry import registry
from ..filters import MapEntityFilterSet
from ..forms import MapEntityForm
from ..serializers import json_django_dumps

logger = logging.getLogger(__name__)


class HttpJSONResponse(HttpResponse):
    def __init__(self, content='', **kwargs):
        kwargs['content_type'] = kwargs.get('content_type', 'application/json')
        super(HttpJSONResponse, self).__init__(content, **kwargs)


class JSONResponseMixin(object):
    """
    A mixin that can be used to render a JSON/JSONP response.
    """
    response_class = HttpJSONResponse

    def render_to_response(self, context, **response_kwargs):
        """
        Returns a JSON response, transforming 'context' to make the payload.
        """
        json = self.convert_context_to_json(context)
        # If callback is specified, serve as JSONP
        callback = self.request.GET.get('callback', None)
        if callback:
            response_kwargs['content_type'] = 'application/javascript'
            json = u"%s(%s);" % (callback, json)
        return self.response_class(json, **response_kwargs)

    def convert_context_to_json(self, context):
        "Convert the context dictionary into a JSON object"
        return json_django_dumps(context)


class LastModifiedMixin(object):
    def dispatch(self, *args, **kwargs):
        qs = self.queryset if self.queryset is not None else self.model.objects
        model = self.model if self.model is not None else self.queryset.model
        try:
            obj = qs.get(pk=kwargs['pk'])
        except (KeyError, model.DoesNotExist):
            return HttpResponseNotFound()

        @cache_last_modified(lambda request, *args, **kwargs: obj.get_date_update())
        def _dispatch(*args, **kwargs):
            return super(LastModifiedMixin, self).dispatch(*args, **kwargs)
        return _dispatch(*args, **kwargs)


class ModelViewMixin(object):
    """
    Add model meta information in context data
    """

    @classmethod
    def get_entity_kind(self):
        return None

    def get_title(self):
        return None

    def get_model(self):
        return self.model or self.queryset.model

    def get_view_perm(self):
        model = self.get_model()
        return model.get_permission_codename(self.get_entity_kind())

    def get_entity(self):
        return registry.registry[self.get_model()]

    def get_context_data(self, **kwargs):
        context = super(ModelViewMixin, self).get_context_data(**kwargs)
        context['viewname'] = self.get_entity_kind()
        context['title'] = self.get_title()

        model = self.get_model()
        if model:
            context['model'] = model
            context['appname'] = model._meta.app_label.lower()
            context['modelname'] = model._meta.object_name.lower()
            context['objectname'] = model._meta.verbose_name
            context['objectsname'] = model._meta.verbose_name_plural
        return context


class FormViewMixin(object):
    """
    Dynamically create form if not specified
    """

    def get_form_class(self):
        if not self.form_class:
            _model = self.model

            class MapEntityAutoForm(MapEntityForm):
                class Meta:
                    model = _model
                    fields = '__all__'
            self.form_class = MapEntityAutoForm
        return self.form_class


class FilterListMixin(object):

    filterform = None

    def __init__(self):

        _model = self.model
        if _model is None:
            _model = self.queryset.model

        if self.filterform is None:
            class filterklass(MapEntityFilterSet):
                class Meta:
                    model = _model
                    fields = [field.name for field in _model._meta.get_fields() if
                              not isinstance(field, GeometryField) and not isinstance(field, GenericRelation)]
            self.filterform = filterklass
        self._filterform = self.filterform(None, self.queryset)

    def get_queryset(self):
        queryset = super(FilterListMixin, self).get_queryset()
        # Filter queryset from possible serialized form
        self._filterform = self.filterform(self.request.GET or None,
                                           queryset=queryset)
        return self._filterform.qs
