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

    class Meta:
        exclude = ('deleted',)  # TODO


class InfrastructureForm(BaseInfrastructureForm):
    class Meta:
        model = Infrastructure


class SignageForm(BaseInfrastructureForm):
    class Meta:
        model = Signage
