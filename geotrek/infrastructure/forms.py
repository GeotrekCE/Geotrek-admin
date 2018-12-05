from django.conf import settings
from django import forms
from geotrek.core.forms import TopologyForm
from geotrek.core.widgets import PointTopologyWidget

from .models import Infrastructure, Signage
from django.utils.translation import ugettext_lazy as _


class BaseInfrastructureForm(TopologyForm):
    implantation_year = forms.IntegerField(label=_(u"Implantation year"), required=False)

    class Meta(TopologyForm.Meta):
        fields = TopologyForm.Meta.fields + \
            ['structure',
             'name', 'description', 'type', 'condition', 'implantation_year']

    def __init__(self, *args, **kwargs):
        super(BaseInfrastructureForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            structure = self.instance.structure
        else:
            structure = self.user.profile.structure
        self.fields['type'].queryset = structure.infrastructuretype_set.all()
        self.fields['condition'].queryset = structure.infrastructurecondition_set.all()


class InfrastructureForm(BaseInfrastructureForm):
    def __init__(self, *args, **kwargs):
        super(InfrastructureForm, self).__init__(*args, **kwargs)
        typefield = self.fields['type']
        typefield.queryset = typefield.queryset.for_infrastructures()

    class Meta(BaseInfrastructureForm.Meta):
        model = Infrastructure


class SignageForm(BaseInfrastructureForm):
    def __init__(self, *args, **kwargs):
        super(SignageForm, self).__init__(*args, **kwargs)
        typefield = self.fields['type']
        typefield.queryset = typefield.queryset.for_signages()

        if not settings.SIGNAGE_LINE_ENABLED:
            self.fields['topology'].widget = PointTopologyWidget()

    class Meta(BaseInfrastructureForm.Meta):
        model = Signage
