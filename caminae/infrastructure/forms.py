from django import forms
from caminae.core.forms import TopologyForm
from caminae.core.widgets import PointTopologyWidget

from .models import Infrastructure, InfrastructureType, Signage


class BaseInfrastructureForm(TopologyForm):
    modelfields = ('name',
                   'description',
                   'type',)


class InfrastructureForm(BaseInfrastructureForm):
    def __init__(self, *args, **kwargs):
        super(InfrastructureForm, self).__init__(*args, **kwargs)
        qs = InfrastructureType.objects.for_infrastructures()
        self.fields['type'] = forms.ModelChoiceField(queryset=qs)

    class Meta(BaseInfrastructureForm.Meta):
        model = Infrastructure


class SignageForm(BaseInfrastructureForm):
    def __init__(self, *args, **kwargs):
        super(SignageForm, self).__init__(*args, **kwargs)
        self.fields['topology'].widget = PointTopologyWidget()
        qs = InfrastructureType.objects.for_signages()
        self.fields['type'] = forms.ModelChoiceField(queryset=qs)

    class Meta(BaseInfrastructureForm.Meta):
        model = Signage
