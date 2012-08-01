from django.forms import ModelForm
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

import floppyforms as forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Submit, Div
from crispy_forms.bootstrap import FormActions

from .models import Path
from .widgets import LineStringWidget


class PathForm(ModelForm):
    geom = forms.gis.LineStringField(widget=LineStringWidget)

    helper = FormHelper()
    helper.form_class = 'form-horizontal'
    helper.layout = Layout(
        Div('name',
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
            css_class="span7",),
        FormActions(
            Submit('save_changes', _('Save changes'), css_class="btn-primary"),
            Submit('cancel', 'Cancel'),
            css_class="form-actions span11 ",
        )
    )

    def __init__(self, *args, **kwargs):
        super(PathForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            self.helper.form_action = self.instance.get_update_url()
        else:
            self.helper.form_action = reverse("core:path_add")

    class Meta:
        model = Path
        exclude = ('geom_cadastre',)
