from django.conf import settings
from django.db.models import Q
from django import forms
from django.forms.models import inlineformset_factory
from crispy_forms.layout import Fieldset, Layout, Div, HTML
from django.forms.models import BaseInlineFormSet
from django.utils.translation import ugettext_lazy as _
from geotrek.core.fields import TopologyField
from geotrek.core.widgets import PointTopologyWidget
from geotrek.infrastructure.forms import BaseInfrastructureForm

from .models import Signage, SignageType, Blade, Line
from crispy_forms.helper import FormHelper

LineFormSet = inlineformset_factory(Blade, Line, fields='__all__', extra=1)


class BladeForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(BladeForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout('id', 'number', 'orientation')

    class Meta:
        fields = ('id', 'number', 'orientation')


BladeFormset = inlineformset_factory(Signage, Blade, form=BladeForm, fk_name='signage', extra=2)


class BaseBladeFormset(BaseInlineFormSet):
    context_name = 'baseblade_formset'

    def add_fields(self, form, index):
        super(BaseBladeFormset, self).add_fields(form, index)
        form.nested = LineFormSet(instance=form.instance, data=form.data if form.is_bound else None,
                                  extra=1)

    def is_valid(self):
        result = super(BaseBladeFormset, self).is_valid()

        if self.is_bound:
            for form in self.forms:
                if hasattr(form, 'nested'):
                    result = result and form.nested.is_valid()

        return result

    def save(self, commit=True):

        result = super(BaseBladeFormset, self).save(commit=commit)

        for form in self.forms:
            if hasattr(form, 'nested'):
                if not self._should_delete_form(form):
                    form.nested.save(commit=commit)

        return result

    class Meta:
        fields = ('id', 'number', 'orientation')


class SignageForm(BaseInfrastructureForm):
    topology = TopologyField(label="")
    fieldslayout = [
        Div(
            Div(
                Div(*(BaseInfrastructureForm.Meta.fields + ['code', 'printed_elevation', 'manager', 'sealing']),
                    css_class="span6"),
                Div(Fieldset(_("Blades")),
                    css_class="span6"),
                css_class="row-fluid"
            ),
            css_class="container-fluid"
        ),
    ]

    def __init__(self, *args, **kwargs):
        super(SignageForm, self).__init__(*args, **kwargs)
        self.helper.form_tag = False

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

    class Meta(BaseInfrastructureForm.Meta):
        model = Signage
        fields = BaseInfrastructureForm.Meta.fields + ['code', 'printed_elevation', 'manager', 'sealing']
