from django import forms
from django.conf import settings
from django.db.models import Max
from django.forms.models import inlineformset_factory
from django.utils.translation import ugettext_lazy as _

from crispy_forms.layout import Layout
from crispy_forms.helper import FormHelper

from geotrek.common.forms import CommonForm
from geotrek.core.fields import TopologyField
from geotrek.core.widgets import PointTopologyWidget
from geotrek.infrastructure.forms import BaseInfrastructureForm
from geotrek.signage.models import Signage, Blade, Line


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

    def save(self, *args, **kwargs):
        self.instance.structure = self.instance.blade.structure
        return super(LineForm, self).save(*args, **kwargs)

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
        value_max = self.signage.blade_set.existing().aggregate(max=Max('number'))['max']
        if settings.BLADE_CODE_TYPE == int:
            if not value_max:
                self.fields['number'].initial = "1"
            elif value_max.isdigit():
                self.fields['number'].initial = str(int(value_max) + 1)
        elif settings.BLADE_CODE_TYPE in (str, unicode):
            if not value_max:
                self.fields['number'].initial = "A"
            elif len(value_max) == 1 and "A" <= value_max[0] < "Z":
                self.fields['number'].initial = chr(ord(value_max[0]) + 1)

    def save(self, *args, **kwargs):
        self.instance.set_topology(self.signage)
        self.instance.signage = self.signage
        self.instance.structure = self.signage.structure
        return super(BladeForm, self).save(*args, **kwargs)

    def clean_number(self):
        blades = self.signage.blade_set.existing()
        if self.instance.pk:
            blades = blades.exclude(number=self.instance.number)
        already_used = ', '.join([str(number) for number in blades.values_list('number', flat=True)])
        if blades.filter(number=self.cleaned_data['number']).exists():
            raise forms.ValidationError(_("Number already exists, numbers already used : %s" % already_used))
        return self.cleaned_data['number']

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
        self.helper.form_tag = False

    def save(self, *args, **kwargs):
        # Fix blade and line structure if signage structure change
        blades = self.instance.blade_set.all()
        blades.update(structure=self.instance.structure)
        Line.objects.filter(blade__in=blades).update(structure=self.instance.structure)
        return super(SignageForm, self).save(*args, **kwargs)

    class Meta(BaseInfrastructureForm.Meta):
        model = Signage
        fields = BaseInfrastructureForm.Meta.fields + ['code', 'printed_elevation', 'manager', 'sealing']
