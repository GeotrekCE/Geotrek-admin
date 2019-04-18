from django import forms
from django.db.models import Q
from geotrek.core.forms import TopologyForm

from .models import Infrastructure
from django.utils.translation import ugettext_lazy as _


class BaseInfrastructureForm(TopologyForm):
    implantation_year = forms.IntegerField(label=_(u"Implantation year"), required=False)

    class Meta(TopologyForm.Meta):
        fields = TopologyForm.Meta.fields + \
            ['structure', 'name', 'description', 'type', 'condition', 'implantation_year', 'published']


class InfrastructureForm(BaseInfrastructureForm):
    class Meta(BaseInfrastructureForm.Meta):
        model = Infrastructure
