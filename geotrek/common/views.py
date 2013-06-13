import json
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponse
from django.views.generic import TemplateView
from django.http import HttpResponseRedirect
from django.core.exceptions import ValidationError
from django.conf import settings

from mapentity.views import HttpJSONResponse

from geotrek import __version__


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


#
# Concrete views
#..............................


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

    return HttpJSONResponse(json.dumps(dictsettings))
