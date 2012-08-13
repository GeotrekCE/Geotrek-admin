import floppyforms as forms

from caminae.core.forms import MapEntityForm
from caminae.core.widgets import PointWidget, MultiPathWidget

from .models import Trek


class TrekForm(MapEntityForm):
    parking_location = forms.gis.GeometryField(widget=PointWidget)
    geom = forms.gis.GeometryField(widget=MultiPathWidget)

    modelfields = (
            'name',
            'departure',
            'arrival',
            'validated',
            'description_teaser',
            'description',
            'ambiance',
            'difficulty',
            'destination',
            'handicapped_infrastructure',
            'duration',
            'is_park_centered',
            'is_transborder',
            'advised_parking',
            'parking_location',
            'public_transport',
            'advice',
            'networks',
            'usages',
            'web_links',
            )
    geomfields = ('geom', )

    class Meta:
        model = Trek
        exclude = ('deleted', 'paths')  # TODO
