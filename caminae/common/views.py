from django.core.serializers import serialize
from django.core.serializers.json import DateTimeAwareJSONEncoder
from django.core.urlresolvers import reverse_lazy
from django.db.models.query import QuerySet
from django.http import HttpResponse
from django.utils.encoding import force_unicode
from django.utils.functional import Promise, curry
from django.utils import simplejson
from django.views.generic import TemplateView
from django.views.generic.list import ListView
from django.http import HttpResponseRedirect
from django.core.exceptions import ValidationError
from django.conf import settings


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


class JSONListView(JSONResponseMixin, ListView):
    """
    A generic view to serve a model as a layer.
    """
    pass


class FormsetMixin(object):
    context_name = None
    formset_class = None

    def form_valid(self, form):
        context = self.get_context_data()
        formset_form = context[self.context_name]
        
        if formset_form.is_valid():
            self.object = form.save()
            formset_form.instance = self.object
            formset_form.save()
            return HttpResponseRedirect(self.get_success_url())
        else:
            return self.render_to_response(self.get_context_data(form=form))

    def get_context_data(self, **kwargs):
        context = super(FormsetMixin, self).get_context_data(**kwargs)
        if self.request.POST:
            try:
                context[self.context_name] = self.formset_class(self.request.POST, instance=self.object)
            except ValidationError:
                pass
        else:
            context[self.context_name] = self.formset_class(instance=self.object)
        return context


# Templates for QUnit testing
class QUnitView(TemplateView):
    template_name = "common/qunit/test_base.html"
    jsfiles = []

    def get_context_data(self, **kwargs):
        context = super(QUnitView, self).get_context_data(**kwargs)
        context['jsfiles'] = self.jsfiles
        return context


#
# Concrete views
#..............................


# Declare JS tests here
# TODO REFACTOR : this is wrong, common should not depend on other apps
qunit_views = dict(
    dijkstra=QUnitView.as_view(jsfiles=['core/dijkstra.js', 'core/test_dijkstra.js']),
    utils=QUnitView.as_view(jsfiles=['mapentity/test_utils.js']),
)


# Reversing directly function using qunit_views.values() does not work, eg:
# [ reverse_lazy(qunit_view) for qunit_view in qunit_views.values() ]
qunit_views_urls = dict((name, reverse_lazy('common:jstest_%s' % name )) for name in qunit_views.keys())

def qunit_tests_list_json(request):
    """List all urls that may be test by an headless browser"""
    return HttpResponse(json_django_dumps(qunit_views_urls), content_type='application/json')



def settings_json(request):
    dictsettings = {}
    # 
    dictsettings['map'] = dict(
        extent=settings.LEAFLET_CONFIG.get('SPATIAL_EXTENT')
    )
    # Languages
    dictsettings['languages'] = dict(available=dict(settings.LANGUAGES),
                                     default=settings.LANGUAGE_CODE)
    return HttpJSONResponse(json_django_dumps(dictsettings))
