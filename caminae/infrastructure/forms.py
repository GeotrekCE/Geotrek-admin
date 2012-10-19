from django import forms
from caminae.core.forms import TopologyForm

from .models import Infrastructure, InfrastructureType, Signage


class BaseInfrastructureForm(TopologyForm):
    modelfields = (
            'name',
            'description',
            'type',)


class InfrastructureForm(BaseInfrastructureForm):
    def __init__(self, *args, **kwargs):
        super(InfrastructureForm, self).__init__(*args, **kwargs)
        self.fields['type'] = forms.ModelChoiceField(
                    queryset=InfrastructureType.objects.for_infrastructures())

    class Meta(BaseInfrastructureForm.Meta):
        model = Infrastructure


class SignageForm(BaseInfrastructureForm):
    def __init__(self, *args, **kwargs):
        super(SignageForm, self).__init__(*args, **kwargs)
        self.fields['type'] = forms.ModelChoiceField(
                    queryset=InfrastructureType.objects.for_signages())

    class Meta(BaseInfrastructureForm.Meta):
        model = Signage
