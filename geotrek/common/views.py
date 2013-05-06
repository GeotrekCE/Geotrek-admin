from django.utils import simplejson
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponse
from django.views.generic import TemplateView
from django.http import HttpResponseRedirect
from django.core.exceptions import ValidationError
from django.conf import settings

from geotrek import __version__
from geotrek.mapentity.views import HttpJSONResponse, json_django_dumps


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
qunit_views_urls = dict((name, reverse_lazy('common:jstest_%s' % name)) for name in qunit_views.keys())


def qunit_tests_list_json(request):
    """List all urls that may be test by an headless browser"""
    return HttpResponse(json_django_dumps(qunit_views_urls), content_type='application/json')


def settings_json(request):
    dictsettings = {}
    dictsettings['map'] = dict(
        extent=settings.LEAFLET_CONFIG.get('SPATIAL_EXTENT'),
        snap_distance=settings.SNAP_DISTANCE,
        styles=settings.MAP_STYLES,
        colorspool=settings.LAND_COLORS_POOL,
    )
    dictsettings['server'] = settings.ROOT_URL if settings.ROOT_URL.endswith('/') else settings.ROOT_URL + '/'
    dictsettings['version'] = __version__
    dictsettings['date_format'] = settings.DATE_INPUT_FORMATS[0].replace('%Y', 'yyyy').replace('%m', 'mm').replace('%d', 'dd')

    # Languages
    dictsettings['languages'] = dict(available=dict(settings.LANGUAGES),
                                     default=settings.LANGUAGE_CODE)

    return HttpJSONResponse(simplejson.dumps(dictsettings))
