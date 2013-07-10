from django import forms
from django.utils.translation import ugettext_lazy as _
from django.forms import FloatField
from django.forms.models import inlineformset_factory

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Fieldset, Layout, Div, HTML

from geotrek.common.forms import CommonForm
from geotrek.core.fields import TopologyField
from geotrek.core.forms import TopologyForm
from geotrek.core.widgets import TopologyReadonlyWidget
from geotrek.infrastructure.models import BaseInfrastructure

from .models import Intervention, Project


class ManDayForm(forms.ModelForm):
    helper = FormHelper()

    def __init__(self, *args, **kwargs):
        super(ManDayForm, self).__init__(*args, **kwargs)
        self.helper.form_tag = False
        self.helper.layout = Layout('id', 'nb_days', 'job')
        self.fields['nb_days'].widget.attrs['placeholder'] = _('Days')
        self.fields['nb_days'].label = ''
        self.fields['nb_days'].widget.attrs['class'] = 'input-mini'
        self.fields['job'].widget.attrs['class'] = 'input-medium'


ManDayFormSet = inlineformset_factory(Intervention, Intervention.jobs.through, form=ManDayForm, extra=1)


class FundingForm(forms.ModelForm):
    helper = FormHelper()

    def __init__(self, *args, **kwargs):
        super(FundingForm, self).__init__(*args, **kwargs)
        self.helper.form_tag = False
        self.helper.layout = Layout('id', 'amount', 'organism')
        self.fields['organism'].widget.attrs['class'] = 'input-xlarge'


FundingFormSet = inlineformset_factory(Project, Project.founders.through, form=FundingForm, extra=1)


class InterventionForm(CommonForm):
    """ An intervention can be a Point or a Line """
    topology = TopologyField(label="")
    infrastructure = forms.ModelChoiceField(required=False,
                                            queryset=BaseInfrastructure.objects.existing(),
                                            widget=forms.HiddenInput())
    length = forms.FloatField(required=False, label=_("Length"))
    modelfields = (
        Div(
            HTML("""
            <ul class="nav nav-tabs">
                <li id="tab-main" class="active"><a href="#main" data-toggle="tab"><i class="icon-certificate"></i> %s</a></li>
                <li id="tab-advanced"><a href="#advanced" data-toggle="tab"><i class="icon-tasks"></i> %s</a></li>
            </ul>""" % (unicode(_("Main")), unicode(_("Advanced")))),
            Div(
                Div(
                    'name',
                    'date',
                    'status',
                    'disorders',
                    'type',
                    'comments',
                    'in_maintenance',
                    'length',
                    'width',
                    'height',
                    'stake',
                    'project',
                    'infrastructure',
                    css_id="main",
                    css_class="tab-pane active"
                ),
                Div(
                    'material_cost',
                    'heliport_cost',
                    'subcontract_cost',
                    Fieldset(_("Mandays")),
                    css_id="advanced",  # used in Javascript for activating tab if error
                    css_class="tab-pane"
                ),
                css_class="tab-content"
            ),
            css_class="tabbable"
        ),
    )

    geomfields = ('topology',)

    class Meta(CommonForm.Meta):
        model = Intervention
        exclude = ('deleted', 'geom', 'jobs')

    MEDIA_JS = TopologyForm.MEDIA_JS

    def __init__(self, *args, **kwargs):
        super(InterventionForm, self).__init__(*args, **kwargs)
        # If we create or edit an intervention on infrastructure, set
        # topology field as read-only
        infrastructure = kwargs.get('initial', {}).get('infrastructure')
        if self.instance.on_infrastructure:
            infrastructure = self.instance.infrastructure
            self.fields['infrastructure'].initial = infrastructure
        if infrastructure:
            self.helper.form_action += '?infrastructure=%s' % infrastructure.pk
            self.fields['topology'].required = False
            self.fields['topology'].widget = TopologyReadonlyWidget()
            self.fields['topology'].label = '%s%s %s' % (
                self.instance.infrastructure_display,
                unicode(_("On %s") % _(infrastructure.kind.lower())),
                u'<a href="%s">%s</a>' % (infrastructure.get_detail_url(), unicode(infrastructure))
            )
        # Length is not editable in AltimetryMixin
        self.fields['length'].initial = self.instance.length
        editable = bool(self.instance.geom and self.instance.geom.geom_type == 'Point')
        self.fields['length'].widget.attrs['readonly'] = editable

    def clean(self, *args, **kwargs):
        # If topology was read-only, topology field is empty, get it from infra.
        cleaned_data = super(InterventionForm, self).clean()
        topology_readonly = self.cleaned_data.get('topology', None) is None
        if topology_readonly and 'infrastructure' in self.cleaned_data:
            self.cleaned_data['topology'] = self.cleaned_data['infrastructure']
        return cleaned_data

    def save(self, *args, **kwargs):
        self.instance.length = self.cleaned_data.get('length')
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
            'height',
            'width',
            'material_cost',
            'heliport_cost',
            'subcontract_cost',
            'stake',
            'project',)


class ProjectForm(CommonForm):
    modelfields = (
        Div(
            Div(
                Div('name',
                    'type',
                    'domain',
                    'begin_year',
                    'end_year',
                    'constraint',
                    'cost',
                    'comments',
                    css_class="span6"),
                Div('project_owner',
                    'project_manager',
                    'contractors',
                    Fieldset(_("Fundings")),
                    css_class="span6"),
                css_class="row-fluid"
            ),
            css_class="container-fluid"
        ),
    )

    class Meta:
        model = Project
        exclude = ('deleted', 'founders')

    def __init__(self, *args, **kwargs):
        super(ProjectForm, self).__init__(*args, **kwargs)
        self.helper.form_tag = False
