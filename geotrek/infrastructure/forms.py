from django import forms
from django.db.models import Q
from geotrek.core.forms import TopologyForm

from .models import Infrastructure, InfrastructureType, InfrastructureCondition
from django.utils.translation import ugettext_lazy as _


class BaseInfrastructureForm(TopologyForm):
    implantation_year = forms.IntegerField(label=_(u"Implantation year"), required=False)

    class Meta(TopologyForm.Meta):
        fields = TopologyForm.Meta.fields + \
            ['name', 'description', 'type', 'condition', 'implantation_year', 'published']


class InfrastructureForm(BaseInfrastructureForm):
    def __init__(self, *args, **kwargs):
        super(InfrastructureForm, self).__init__(*args, **kwargs)

        if self.instance.pk:
            structure = self.instance.structure
        else:
            structure = self.user.profile.structure
        self.fields['type'].queryset = InfrastructureType.objects.filter(Q(structure=structure) | Q(structure=None))
        self.fields['condition'].queryset = InfrastructureCondition.objects.filter(
            Q(structure=structure) | Q(structure=None))

    class Meta(BaseInfrastructureForm.Meta):
        model = Infrastructure
