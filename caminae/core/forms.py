from django.forms import ModelForm
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.contrib.gis.geos import fromstr
from django.conf import settings

import floppyforms as forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Submit, Div
from crispy_forms.bootstrap import FormActions

from .models import Path


class OsmLineStringWidget(forms.gis.BaseMetacartaWidget,
                          forms.gis.LineStringWidget):
    def value_from_datadict(self, data, files, name):
        wkt = super(OsmLineStringWidget, self).value_from_datadict(data, files, name)
        # TODO : transform here ?
        geom = fromstr(wkt)
        geom.transform(settings.SRID)
        wkt3d = geom.wkt.replace(',', ' 0.0,')  # TODO: woot!
        return wkt3d


class PathForm(ModelForm):
    geom = forms.gis.LineStringField(widget=OsmLineStringWidget)

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
