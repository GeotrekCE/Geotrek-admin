from math import isnan

from django.forms import ModelForm
from django.contrib.gis.geos import LineString
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

import floppyforms as forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Submit, Div, Button
from crispy_forms.bootstrap import FormActions

from .models import Path
from .widgets import LineStringWidget


class PathForm(ModelForm):
    pk = forms.Field(required=False, widget=forms.Field.hidden_widget)

    geom = forms.gis.LineStringField(widget=LineStringWidget)

    reverse_geom = forms.BooleanField(
           required=False,
           label = _("Reverse path"),
           help_text = _("The path will be reversed once saved"),
       )

    helper = FormHelper()
    helper.form_class = 'form-horizontal'
    helper.layout = Layout(
        Div('pk',
            'name',
            'structure',
            'stake',
            'trail',
            Field('comments', css_class='input-xlarge'),
            'datasource',
            'networks',
            'usages',
            'valid',
            
            css_class="span4",
        ),
        Div('geom',
            'reverse_geom',
            css_class="span7",),
        FormActions(
            Button('cancel', _('Cancel'), ),
            Submit('save_changes', _('Save changes'), css_class="btn-primary offset1"),
            css_class="form-actions span11",
        )
    )

    def __init__(self, *args, **kwargs):
        super(PathForm, self).__init__(*args, **kwargs)

        if self.instance.pk:
            self.helper.form_action = self.instance.get_update_url()
        else:
            self.helper.form_action = reverse("core:path_add")

        self.fields['pk'].initial = self.instance.pk

    def save(self, commit=True):
        path = super(PathForm, self).save(commit=False)

        if self.cleaned_data.get('reverse_geom'):
            # path.geom.reverse() won't work for 3D coords
            reversed_coord = path.geom.coords[-1::-1]
            # FIXME: why do we have to filter nan variable ?! Why are they here in the first place ?
            valid_coords = [ (x, y, 0.0 if isnan(z) else z) for x, y, z in reversed_coord ]
            path.geom = LineString(valid_coords)

        if commit:
            path.save()

        return path

    class Meta:
        model = Path
        exclude = ('geom_cadastre',)
