from django import forms
from django.utils.translation import ugettext_lazy as _

from crispy_forms.layout import Field

from caminae.common.forms import CommonForm
from caminae.core.fields import TopologyField
from caminae.core.widgets import TopologyReadonlyWidget
from caminae.infrastructure.models import BaseInfrastructure

from .models import Intervention, Project


class InterventionForm(CommonForm):
    """ An intervention can be a Point or a Line """
    topology = TopologyField()
    infrastructure = forms.ModelChoiceField(required=False,
                                            queryset=BaseInfrastructure.objects.all(),
                                            widget=forms.HiddenInput())
    modelfields = (
            'name',
            'date',
            'status',
            'disorders',
            'type',
            Field('comments', css_class='input-xlarge'),
            'in_maintenance',
            'length',
            'height',
            'width',
            'area',
            'slope',
            'material_cost',
            'heliport_cost',
            'subcontract_cost',
            'stake',
            'project',
            'infrastructure',)
    geomfields = ('topology',)

    class Meta:
        model = Intervention
        exclude = ('deleted', 'geom', 'jobs')  # TODO: inline formset for jobs

    def __init__(self, *args, **kwargs):
        super(InterventionForm, self).__init__(*args, **kwargs)
        # If we create or edit an intervention on infrastructure, set
        # topology field as read-only
        infrastructure = kwargs.get('initial', {}).get('infrastructure')
        if self.instance.on_infrastructure:
            infrastructure = self.instance.topology
        if infrastructure:
            self.helper.form_action += '?infrastructure=%s' % infrastructure.pk
            self.fields['topology'].widget = TopologyReadonlyWidget()
            self.fields['topology'].label = _(infrastructure.kind.kind)

    def clean(self, *args, **kwargs):
        # If topology was read-only, topology field is empty, get it from infra.
        cleaned_data = super(InterventionForm, self).clean()
        if 'infrastructure' in self.cleaned_data and \
           'topology' not in self.cleaned_data:
            self.cleaned_data['topology'] = self.cleaned_data['infrastructure']
        return cleaned_data

    def save(self, *args, **kwargs):
        infrastructure = self.cleaned_data.get('infrastructure')
        if infrastructure:
            self.instance.set_infrastructure(infrastructure)
        return super(InterventionForm, self).save(*args, **kwargs)


class InterventionCreateForm(InterventionForm):
    def __init__(self, *args, **kwargs):
        # If we create an intervention on infrastructure, get its topology
        initial = kwargs.get('initial', {})
        infrastructure = initial.get('infrastructure')
        if infrastructure:
            initial['topology'] = infrastructure
        kwargs['initial'] = initial
        super(InterventionCreateForm, self).__init__(*args, **kwargs)

    class Meta(InterventionForm.Meta):
        exclude = InterventionForm.Meta.exclude + (
            'length',
            'height',
            'width',
            'area',
            'slope',
            'material_cost',
            'heliport_cost',
            'subcontract_cost',
            'stake',
            'project', )


class ProjectForm(CommonForm):
    modelfields = (
            'name',
            'begin_year',
            'end_year',
            'constraint',
            'cost',
            Field('comments', css_class='input-xlarge'),
            'contractors',
            'project_owner',
            'project_manager',
            'founders',)
    geomfields = tuple()  # no geom field in project

    class Meta:
        model = Project
        exclude = ('deleted', 'founders',)  #TODO founders (inline form)
