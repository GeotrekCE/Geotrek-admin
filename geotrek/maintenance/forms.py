from django import forms
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.forms import FloatField
from django.utils.translation import ugettext_lazy as _
from django.forms.models import inlineformset_factory

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Fieldset, Layout, Div, HTML

from geotrek.common.forms import CommonForm
from geotrek.core.fields import TopologyField
from geotrek.core.widgets import TopologyReadonlyWidget
from geotrek.maintenance.widgets import InterventionWidget

from .models import Intervention, Project


class ManDayForm(forms.ModelForm):

    class Meta:
        fields = ('id', 'nb_days', 'job')

    def __init__(self, *args, **kwargs):
        super(ManDayForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout('id', 'nb_days', 'job')
        self.fields['nb_days'].widget.attrs['placeholder'] = _('Days')
        self.fields['nb_days'].label = ''
        self.fields['nb_days'].widget.attrs['class'] = 'input-mini'
        self.fields['job'].widget.attrs['class'] = 'input-medium'


ManDayFormSet = inlineformset_factory(Intervention, Intervention.jobs.through, form=ManDayForm, extra=1)


class FundingForm(forms.ModelForm):

    class Meta:
        fields = ('id', 'amount', 'organism')

    def __init__(self, *args, **kwargs):
        super(FundingForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout('id', 'amount', 'organism')
        self.fields['organism'].widget.attrs['class'] = 'input-xlarge'


FundingFormSet = inlineformset_factory(Project, Project.founders.through, form=FundingForm, extra=1)


class InterventionBaseForm(CommonForm):
    object_id = forms.IntegerField(required=False,
                                   widget=forms.HiddenInput())
    content_type = forms.ModelChoiceField(required=False,
                                          queryset=ContentType.objects.all(),
                                          widget=forms.HiddenInput())
    length = FloatField(required=False, label=_("Length"))
    project = forms.ModelChoiceField(required=False, label=_("Project"),
                                     queryset=Project.objects.existing())
    geomfields = ['topology']
    leftpanel_scrollable = False

    topology = TopologyField(label="")

    fieldslayout = [
        Div(
            HTML("""
               <ul class="nav nav-tabs">
                   <li id="tab-main" class="active"><a href="#main" data-toggle="tab"><i class="icon-certificate"></i> %s</a></li>
                   <li id="tab-advanced"><a href="#advanced" data-toggle="tab"><i class="icon-tasks"></i> %s</a></li>
               </ul>""" % (_("Main"), _("Advanced"))),
            Div(
                Div(
                    'structure',
                    'name',
                    'date',
                    'status',
                    'disorders',
                    'type',
                    'subcontracting',
                    'length',
                    'width',
                    'height',
                    'stake',
                    'project',
                    'description',
                    'content_type',
                    'object_id',
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
                css_class="scrollable tab-content"
            ),
            css_class="tabbable"
        ),
    ]

    class Meta(CommonForm.Meta):
        model = Intervention
        fields = CommonForm.Meta.fields + \
            ['structure', 'name', 'date', 'status', 'disorders', 'type', 'description', 'subcontracting', 'length', 'width',
             'height', 'stake', 'project', 'material_cost', 'heliport_cost', 'subcontract_cost',
             'topology', 'content_type', 'object_id']


if settings.TREKKING_TOPOLOGY_ENABLED:
    class InterventionForm(InterventionBaseForm):
        """ An intervention can be a Point or a Line """

        def __init__(self, *args, **kwargs):
            super(InterventionForm, self).__init__(*args, **kwargs)
            # If we create or edit an intervention on infrastructure or signage, set
            # topology field as read-only
            object_linked = kwargs.get('initial', {}).get('object_linked')
            if self.instance.on_existing_topology:
                if self.instance.infrastructure:
                    infrastructure = self.instance.infrastructure
                    self.fields['content_type'].initial = ContentType.objects.get_for_model(object_linked)
                    self.fields['object_id'].initial = object_linked
                elif self.instance.signage:
                    signage = self.instance.signage
                    self.fields['content_type'].initial = ContentType.objects.get_for_model(object_linked)
                    self.fields['object_id'].initial = object_linked
            if object_linked:
                self.helper.form_action += '?infrastructure=%s' % object_linked.pk
                self.fields['topology'].required = False
                self.fields['topology'].widget = TopologyReadonlyWidget()
                self.fields['topology'].label = '%s%s %s' % (
                    self.instance.infrastructure_display,
                    _("On %s") % _(object_linked.kind.lower()),
                    '<a href="%s">%s</a>' % (object_linked.get_detail_url(), str(object_linked))
                )
                self.fields['content_type'].initial = ContentType.objects.get_for_model(object_linked)
                self.fields['object_id'].initial = object_linked.pk
            print(self.fields['content_type'].initial, self.fields['object_id'].initial)
            # Length is not editable in AltimetryMixin
            self.fields['length'].initial = self.instance.length
            editable = bool(self.instance.geom and self.instance.geom.geom_type == 'Point')
            self.fields['length'].widget.attrs['readonly'] = editable

        def clean(self, *args, **kwargs):
            # If topology was read-only, topology field is empty, get it from infra.
            cleaned_data = super(InterventionForm, self).clean()
            topology_readonly = self.cleaned_data.get('topology', None) is None
            if topology_readonly:
                self.cleaned_data['topology'] = self.cleaned_data['object_id']
            return cleaned_data

        def save(self, *args, **kwargs):
            infrastructure = self.cleaned_data.get('infrastructure')
            signage = self.cleaned_data.get('signage')
            if infrastructure:
                self.instance.set_topology(infrastructure)
            elif signage:
                self.instance.set_topology(signage)
            return super(InterventionForm, self).save(*args, **kwargs)
else:
    class InterventionForm(InterventionBaseForm):
        """ An intervention can be a Point or a Line """

        def __init__(self, *args, **kwargs):
            super(InterventionForm, self).__init__(*args, **kwargs)
            # If we create or edit an intervention on infrastructure or signage, set
            # topology field as read-only
            infrastructure = kwargs.get('initial', {}).get('infrastructure')
            signage = kwargs.get('initial', {}).get('signage')
            if self.instance.on_existing_topology:
                if self.instance.infrastructure:
                    infrastructure = self.instance.infrastructure
                    self.fields['infrastructure'].initial = infrastructure
                elif self.instance.signage:
                    signage = self.instance.signage
                    self.fields['signage'].initial = signage
            if infrastructure:
                self.helper.form_action += '?infrastructure=%s' % infrastructure.pk
                self.fields['topology'].required = False
                self.fields['topology'].widget = TopologyReadonlyWidget()
                self.fields['topology'].widget.modifiable = False
                self.fields['topology'].label = '%s%s %s' % (
                    self.instance.infrastructure_display,
                    _("On %s") % _(infrastructure.kind.lower()),
                    '<a href="%s">%s</a>' % (infrastructure.get_detail_url(), str(infrastructure))
                )
            elif signage:
                self.helper.form_action += '?signage=%s' % signage.pk
                self.fields['topology'].required = False
                self.fields['topology'].widget = TopologyReadonlyWidget()
                self.fields['topology'].label = '%s%s %s' % (
                    self.instance.infrastructure_display,
                    _("On %s") % _(signage.kind.lower()),
                    '<a href="%s">%s</a>' % (signage.get_detail_url(), str(signage))
                )
            else:
                self.fields['topology'].required = False
                self.fields['topology'].widget = InterventionWidget(attrs={'geom_type': 'POINT'})
            # Length is not editable in AltimetryMixin
            self.fields['length'].initial = self.instance.length
            editable = bool(self.instance.geom and self.instance.geom.geom_type == 'Point')
            self.fields['length'].widget.attrs['readonly'] = editable

        def clean(self, *args, **kwargs):
            # If topology was read-only, topology field is empty, get it from infra.
            cleaned_data = super(InterventionForm, self).clean()
            topology_readonly = self.cleaned_data.get('topology', None) is None
            if topology_readonly:
                if 'infrastructure' in self.cleaned_data:
                    self.cleaned_data['topology'] = self.cleaned_data['infrastructure']
                if 'signage' in self.cleaned_data and not self.cleaned_data['topology']:
                    self.cleaned_data['topology'] = self.cleaned_data['signage']
            return cleaned_data

        def save(self, *args, **kwargs):
            infrastructure = self.cleaned_data.get('infrastructure')
            signage = self.cleaned_data.get('signage')
            if infrastructure:
                self.instance.set_topology(infrastructure)
            elif signage:
                self.instance.set_topology(signage)
            return super(InterventionForm, self).save(*args, **kwargs)


class InterventionCreateForm(InterventionForm):
    def __init__(self, *args, **kwargs):
        # If we create an intervention on infrastructure, get its topology
        initial = kwargs.get('initial', {})
        object_linked = initial.get('object_linked')
        if object_linked:
            initial['topology'] = object_linked
        kwargs['initial'] = initial
        super(InterventionCreateForm, self).__init__(*args, **kwargs)


class ProjectForm(CommonForm):
    fieldslayout = [
        Div(
            Div(
                Div('structure',
                    'name',
                    'type',
                    'domain',
                    'begin_year',
                    'end_year',
                    'constraint',
                    'global_cost',
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
    ]

    class Meta(CommonForm.Meta):
        model = Project
        fields = CommonForm.Meta.fields + \
            ['structure', 'name', 'type', 'domain', 'begin_year', 'end_year', 'constraint',
             'global_cost', 'comments', 'project_owner', 'project_manager', 'contractors']

    def __init__(self, *args, **kwargs):
        super(ProjectForm, self).__init__(*args, **kwargs)
        self.helper.form_tag = False
