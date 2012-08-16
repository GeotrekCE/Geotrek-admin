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


class InfrastructureForm(BaseInfrastructureForm):
    class Meta(BaseInfrastructureForm.Meta):
        model = Infrastructure


class SignageForm(BaseInfrastructureForm):
    class Meta(BaseInfrastructureForm.Meta):
        model = Signage
