from caminae.core.forms import TopologyMixinForm

from .models import Infrastructure, Signage


class BaseInfrastructureForm(TopologyMixinForm):
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
