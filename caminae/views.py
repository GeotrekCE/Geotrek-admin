from django.contrib.auth.decorators import login_required
from django.views.generic.simple import direct_to_template

from caminae.maintenance.models import Contractor


@login_required
def home(request):
    # Temporary during Sprint1
    return direct_to_template(request, "home.html", dict(
        contractors=Contractor.forUser(request.user),
        all_contractors=Contractor.objects.all(),
    ))
