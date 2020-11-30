from crispy_forms.layout import Div
from geotrek.common.forms import CommonForm
from geotrek.outdoor.models import Site


class SiteForm(CommonForm):
    geomfields = ['geom']

    fieldslayout = [
        Div(
            'structure',
            'name',
            'description',
            'eid',
        )
    ]

    class Meta:
        fields = ['structure', 'name', 'description', 'geom', 'eid']
        model = Site
