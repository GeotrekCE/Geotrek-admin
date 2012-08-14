import floppyforms as forms

from caminae.mapentity.forms import MapEntityForm
from caminae.core.widgets import PointOrMultipathWidget

from .models import Infrastructure, Signage


class BaseInfrastructureForm(MapEntityForm):
    geom = forms.gis.GeometryField(widget=PointOrMultipathWidget)

    modelfields = (
            'name',
            'description',
            'type',)
    geomfields = ('geom',)


class InfrastructureForm(BaseInfrastructureForm):
    class Meta:
        model = Infrastructure
        exclude = ('deleted',)


class SignageForm(BaseInfrastructureForm):
    class Meta:
        model = Signage
        exclude = ('deleted',)
