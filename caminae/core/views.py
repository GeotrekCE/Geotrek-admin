from django.contrib.auth.decorators import login_required
from django.views.generic.simple import direct_to_template
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_control, cache_page
#
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.detail import DetailView
from django.core.urlresolvers import reverse_lazy, reverse

from djgeojson.views import GeoJSONLayerView

from caminae.maintenance.models import Contractor
from .models import Path


class PathLayer(GeoJSONLayerView):
    model = Path
    fields = ('name', 'valid',)
    precision = 4
    srid = 4326  #TODO: remove and serve in L93
    # simplify = 0.5

    @method_decorator(cache_page(60, cache="fat"))  #TODO: use settings
    @method_decorator(cache_control(max_age=3600*24))   #TODO: use settings
    def dispatch(self, *args, **kwargs):
        return super(PathLayer, self).dispatch(*args, **kwargs)


@login_required
def home(request):
    # Temporary during Sprint1
    return direct_to_template(request, "core/home.html", dict(
        contractors=Contractor.forUser(request.user),
        all_contractors=Contractor.objects.all(),
        all_paths=Path.objects.all()[:20],
    ))


class PathDetail(DetailView):
    model = Path
    context_object_name = 'path'


class PathCreate(CreateView):
    model = Path
    context_object_name = 'path'

    def get_success_url(self):
        return reverse('core:path_detail', kwargs={'pk': self.object.pk})


class PathUpdate(UpdateView):
    model = Path
    context_object_name = 'path'

    def get_success_url(self):
        return reverse('core:path_detail', kwargs={'pk': self.object.pk})

class PathDelete(DeleteView):
    model = Path
    context_object_name = 'path'
    success_url = reverse_lazy('path_list')

# redirect to home for now
path_list = home
