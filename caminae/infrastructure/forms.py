from caminae.core.forms import TopologyMixinForm
from caminae.core.fields import PointLineTopologyField

from .models import Infrastructure, Signage


class BaseInfrastructureForm(TopologyMixinForm):
    """ An infrastructure can be a Point or a Line """
    geom = PointLineTopologyField()

    def clean_geom(self):
        # TODO remove geom, assign topology
        pass

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
