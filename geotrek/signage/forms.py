from django.conf import settings
from django.db.models import Q
from django import forms
from django.forms.models import inlineformset_factory
from crispy_forms.layout import Fieldset, Layout, Div, HTML, Submit
from django.forms.models import BaseInlineFormSet
from django.utils.translation import ugettext_lazy as _
from django.db import transaction
from geotrek.core.fields import TopologyField
from geotrek.core.widgets import PointTopologyWidget
from geotrek.infrastructure.forms import BaseInfrastructureForm
from geotrek.core.widgets import TopologyReadonlyWidget
from geotrek.common.forms import CommonForm
from geotrek.trekking.models import Topology
from .models import Signage, SignageType, Blade, Line
from crispy_forms.helper import FormHelper
from mapentity.forms import SubmitButton


class LineForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(LineForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout('id', 'number', 'text', 'distance', 'pictogram_name', 'time')
        self.fields['number'].widget.attrs['class'] = 'input-mini'
        self.fields['text'].widget.attrs['class'] = 'input-xlarge'
        self.fields['distance'].widget.attrs['class'] = 'input-mini'
        self.fields['pictogram_name'].widget.attrs['class'] = 'input-mini'
        self.fields['time'].widget.attrs['class'] = 'input-mini'

    class Meta:
        fields = ('id', 'number', 'text', 'distance', 'pictogram_name', 'time')


LineFormset = inlineformset_factory(Blade, Line, form=LineForm, extra=1)


class BladeSignageForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(BladeSignageForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout('id', 'number', 'orientation', 'type', 'condition', 'color')
        self.fields['number'].widget.attrs['class'] = 'input-mini'
        self.fields['orientation'].widget.attrs['class'] = 'input-xlarge'
        self.fields['type'].widget.attrs['class'] = 'input-mini'
        self.fields['condition'].widget.attrs['class'] = 'input-mini'

    class Meta:
        fields = ('id', 'number', 'orientation', 'type', 'condition', 'color')


class BladeForm(forms.ModelForm):

    fieldslayout = [
        Div(
            Div(
                Div('number',
                    'orientation',
                    'type',
                    'condition',
                    'color',

                    css_class="span6"),
                Div(
                    Fieldset(_("Lines")),
                    css_class="span6"
                ),
                css_class="row-fluid"
            ),
            css_class="container-fluid"

        ),
    ]

    def __init__(self, *args, **kwargs):
        super(BladeForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False

    def form_valid(self, form):
        context = self.get_context_data()
        print(context)
        familymembers = context['familymembers']
        with transaction.atomic():
            self.object = form.save()

            if familymembers.is_valid():
                familymembers.instance = self.object
                familymembers.save()
        return super(BladeForm, self).form_valid(form)

    class Meta:
        model = Blade
        fields = ('id', 'number', 'orientation', 'type', 'condition', 'color')


BladeFormset = inlineformset_factory(Signage, Blade, form=BladeSignageForm, extra=1)


class SignageForm(BaseInfrastructureForm):
    fieldslayout = [
        Div(
            HTML("""
                        <ul class="nav nav-tabs">
                            <li id="tab-main" class="active"><a href="#main" data-toggle="tab"><i class="icon-certificate"></i> %s</a></li>
                            <li id="tab-blades"><a href="#blades" data-toggle="tab"><i class="icon-tasks"></i> %s</a></li>
                        </ul>""" % (unicode(_("Main")), unicode(_("Blades")))),
            Div(
                Div(
                    Div('name',
                        'type',
                        'condition',
                        'code',
                        'printed_elevation',
                        'manager',
                        'sealing',

                        css_id="main",
                        css_class="tab-pane active"),
                    Div(
                        Fieldset(_("Blades")),
                        css_id="blades",  # used in Javascript for activating tab if error
                        css_class="tab-pane"
                    ),
                    css_class="scrollable tab-content"
                ),
                css_class="tabbable"
            ),
        ),
    ]
    topology = TopologyField(label="")
    leftpanel_scrollable = False
    geomfields = ['topology']

    def __init__(self, *args, **kwargs):
        super(SignageForm, self).__init__(*args, **kwargs)

        if not settings.SIGNAGE_LINE_ENABLED:
            modifiable = self.fields['topology'].widget.modifiable
            self.fields['topology'].widget = PointTopologyWidget()
            self.fields['topology'].widget.modifiable = modifiable

        if self.instance.pk:
            structure = self.instance.structure
        else:
            structure = self.user.profile.structure
        self.fields['type'].queryset = SignageType.objects.filter(Q(structure=structure) | Q(structure=None))
        self.fields['condition'].queryset = structure.infrastructurecondition_set.all()
        self.helper.form_tag = False

    class Meta(BaseInfrastructureForm.Meta):
        model = Signage
        fields = BaseInfrastructureForm.Meta.fields + ['code', 'printed_elevation', 'manager', 'sealing']
