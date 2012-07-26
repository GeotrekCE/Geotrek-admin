from django.contrib.auth.decorators import login_required
from django.views.generic.simple import direct_to_template
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_control, cache_page

from djgeojson.views import GeoJSONLayerView

from caminae.maintenance.models import Contractor
from .models import Path


class PathList(GeoJSONLayerView):
    model = Path
    fields = ('name', 'valid',)
    precision = 4
    srid = 4326  #TODO: remove and serve in L93
    # simplify = 0.5

    @method_decorator(cache_page(60, cache="fat"))  #TODO: use settings
    @method_decorator(cache_control(max_age=3600*24))   #TODO: use settings
    def dispatch(self, *args, **kwargs):
        return super(PathList, self).dispatch(*args, **kwargs)


@login_required
def home(request):
    # Temporary during Sprint1
    return direct_to_template(request, "core/home.html", dict(
        contractors=Contractor.forUser(request.user),
        all_contractors=Contractor.objects.all(),
    ))


