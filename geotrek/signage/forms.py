from django.conf import settings
from django.db.models import Q, Max
from django import forms
from django.forms.models import inlineformset_factory
from crispy_forms.layout import Fieldset, Layout, Div, HTML, Submit
from django.utils.translation import ugettext_lazy as _
from geotrek.core.fields import TopologyField
from geotrek.core.widgets import PointTopologyWidget
from geotrek.infrastructure.forms import BaseInfrastructureForm
from geotrek.core.widgets import TopologyReadonlyWidget, BaseTopologyWidget

from geotrek.common.forms import CommonForm
from .models import Signage, SignageType, Blade, Line
from crispy_forms.helper import FormHelper


class LineForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(LineForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout('id', 'number', 'text', 'distance', 'pictogram_name', 'time')
        self.fields['number'].widget.attrs['class'] = 'input-mini'
        self.fields['text'].widget.attrs['class'] = 'input-xlarge'
        self.fields['distance'].widget.attrs['class'] = 'input-mini'
        self.fields['pictogram_name'].widget.attrs['class'] = 'input-mini'
        self.fields['time'].widget.attrs['class'] = 'input-mini'

    class Meta:
        fields = ('id', 'blade', 'number', 'text', 'distance', 'pictogram_name', 'time')


LineFormset = inlineformset_factory(Blade, Line, form=LineForm, extra=1)


class BladeForm(CommonForm):
    topology = TopologyField(label="")
    geomfields = ['topology']
    leftpanel_scrollable = True

    def __init__(self, *args, **kwargs):
        super(BladeForm, self).__init__(*args, **kwargs)
        self.helper.form_tag = False
        if not self.instance.pk:
            self.signage = kwargs.get('initial', {}).get('signage')
            self.helper.form_action += '?signage=%s' % self.signage.pk
        else:
            self.signage = self.instance.signage
        self.fields['topology'].initial = self.signage
        self.fields['topology'].widget.modifiable = True
        self.fields['topology'].label = '%s%s %s' % (
            self.instance.signage_display,
            unicode(_("On %s") % _(self.signage.kind.lower())),
            u'<a href="%s">%s</a>' % (self.signage.get_detail_url(), unicode(self.signage))
        )
        max_blade = self.signage.blade_set.all().aggregate(max=Max('number'))
        value_max = max_blade['max']

        self.fields['number'].initial = value_max + 1 if value_max else 1

    def save(self, *args, **kwargs):
        self.instance.set_topology(self.signage)
        self.instance.signage = self.signage
        return super(BladeForm, self).save(*args, **kwargs)

    class Meta:
        model = Blade
        fields = ['id', 'number', 'direction', 'type', 'condition', 'color']


class SignageForm(BaseInfrastructureForm):
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
