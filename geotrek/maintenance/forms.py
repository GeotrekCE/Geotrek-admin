from django import forms
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.forms import FloatField
from django.utils.translation import gettext_lazy as _
from django.forms.models import inlineformset_factory
from django.shortcuts import get_object_or_404

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Fieldset, Layout, Div, HTML

from geotrek.common.forms import CommonForm
from geotrek.core.fields import TopologyField
from geotrek.core.models import Topology
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
    target_id = forms.IntegerField(required=False,
                                   widget=forms.HiddenInput())
    target_type = forms.ModelChoiceField(required=False,
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
                    'target_type',
                    'target_id',
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
             'height', 'stake', 'project', 'material_cost', 'heliport_cost', 'subcontract_cost', 'target_type', 'target_id',
             'topology']


class InterventionForm(InterventionBaseForm):
    """ An intervention can be a Point or a Line """

    def __init__(self, *args, **kwargs):
        super(InterventionForm, self).__init__(*args, **kwargs)

        # If we create or edit an intervention on infrastructure or signage, set
        # topology field as read-only
        target_id = kwargs.get('initial', {}).get('target_id')
        target_type = kwargs.get('initial', {}).get('target_type')
        if self.instance.on_existing_target:
            target_id = self.instance.target_id
            target_type = self.instance.target_type.pk
            self.fields['target_type'].initial = target_type
            self.fields['target_id'].initial = target_id

        if target_type and target_id:
            ct = get_object_or_404(ContentType, pk=target_type)

        if target_id:
            final_object = ct.model_class().objects.get(pk=target_id)
            icon = final_object._meta.model_name
            title = '%s' % (_(final_object._meta.model_name).capitalize())
            self.helper.form_action += '?target_id=%s' % target_id
            if final_object._meta.model_name != "topology":
                self.fields['topology'].required = False
                self.fields['topology'].widget = TopologyReadonlyWidget()
                self.fields['topology'].label = '%s%s %s' % (
                    '<img src="%simages/%s-16.png" title="%s">' % (settings.STATIC_URL,
                                                                   icon,
                                                                   title),
                    _("On %s") % _(str(ct)).lower(),
                    '<a href="%s">%s</a>' % (final_object.get_detail_url(),
                                             str(final_object))
                )
            else:
                self.fields['topology'].initial = final_object
                self.fields['topology'].label = '%s%s' % (
                    '<img src="%simages/path-16.png" title="%s">' % (settings.STATIC_URL,
                                                                     title),
                    _("On %s") % _(str(ct)).lower()
                )
            self.fields['target_id'].initial = target_id
            self.fields['target_type'].initial = target_type
        elif not settings.TREKKING_TOPOLOGY_ENABLED:
            self.fields['topology'].required = False
            self.fields['topology'].widget = InterventionWidget(attrs={'geom_type': 'POINT'})
        # Length is not editable in AltimetryMixin
        self.fields['length'].initial = self.instance.length
        editable = bool(self.instance.geom and (self.instance.geom.geom_type == 'Point'
                        or self.instance.geom.geom_type == 'LineString'))
        self.fields['length'].widget.attrs['readonly'] = editable

    def clean(self, *args, **kwargs):
        # If topology was read-only, topology field is empty, get it from infra.
        cleaned_data = super(InterventionForm, self).clean()
        if not cleaned_data.get('target_id') and cleaned_data.get('topology'):
            cleaned_data['target_id'] = cleaned_data['topology'].pk
            ct = ContentType.objects.get_for_model(Topology)
            cleaned_data['target_type'] = ct
        return cleaned_data


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
