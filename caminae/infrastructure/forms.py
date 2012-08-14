import floppyforms as forms

from caminae.core.forms import TopologyMixinForm
from caminae.core.widgets import PointOrMultipathWidget

from .models import Infrastructure, Signage


class BaseInfrastructureForm(TopologyMixinForm):
    geom = forms.gis.GeometryField(widget=PointOrMultipathWidget)

    modelfields = (
            'name',
            'description',
            'type',)
    geomfields = ('geom',)


class InfrastructureForm(BaseInfrastructureForm):
    class Meta:
        model = Infrastructure
        exclude = ('deleted', 'kind', 'troncons', 'offset')  # TODO: topology editor


class SignageForm(BaseInfrastructureForm):
    class Meta:
        model = Signage
        exclude = ('deleted', 'kind', 'troncons', 'offset')
