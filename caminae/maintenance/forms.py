from django import forms
from crispy_forms.layout import Field

from caminae.mapentity.forms import MapEntityForm
from caminae.core.fields import PointLineTopologyField
from caminae.core.widgets import TopologyReadonlyWidget
from caminae.infrastructure.models import Infrastructure

from .models import Intervention, InterventionStatus, Project


class InterventionForm(MapEntityForm):
    """ An intervention can be a Point or a Line """
    topology = PointLineTopologyField()
    infrastructure = forms.ModelChoiceField(required=False,
                                            queryset=Infrastructure.objects.all(),
                                            widget=forms.HiddenInput())
    modelfields = (
            'name',
            'structure',
            'date',
            'status',
            'type',
            'disorders',
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
        initial = kwargs.get('initial', {})
        infrastructure = initial.get('infrastructure')
        if infrastructure:
            initial['topology'] = infrastructure
        kwargs['initial'] = initial
        super(InterventionForm, self).__init__(*args, **kwargs)
        if infrastructure:
            self.fields['topology'].widget = TopologyReadonlyWidget()

    def save(self, *args, **kwargs):
        infrastructure = self.cleaned_data.get('infrastructure')
        if infrastructure:
            self.instance.set_infrastructure(infrastructure)
        return super(InterventionForm, self).save(*args, **kwargs)


class InterventionCreateForm(InterventionForm):
    def __init__(self, *args, **kwargs):
        super(InterventionCreateForm, self).__init__(*args, **kwargs)
        # Limit status choices to first one only ("requested")
        first = InterventionStatus.objects.all()[0]
        self.fields['status'] = forms.ModelChoiceField(queryset=InterventionStatus.objects.filter(pk=first.pk))

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


class ProjectForm(MapEntityForm):
    modelfields = (
            'name',
            'structure',
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
