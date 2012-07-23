from django.contrib.auth.decorators import login_required
from django.views.generic.simple import direct_to_template

from djgeojson.views import GeoJSONLayerView

from caminae.maintenance.models import Contractor
from .models import Path


class PathList(GeoJSONLayerView):
    model = Path
    fields = ('name', 'valid',)
    precision = 2
    srid = 4326
    # simplify = 0.5


@login_required
def home(request):
    # Temporary during Sprint1
    return direct_to_template(request, "core/home.html", dict(
        contractors=Contractor.forUser(request.user),
        all_contractors=Contractor.objects.all(),
    ))
