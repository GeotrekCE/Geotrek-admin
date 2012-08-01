from django.forms import ModelForm

import floppyforms as forms

from .models import Path


class OsmLineStringWidget(forms.gis.BaseOsmWidget,
                          forms.gis.LineStringWidget):
    pass


class PathForm(ModelForm):
    geom = forms.gis.LineStringField(widget=OsmLineStringWidget)
    class Meta:
        model = Path
        exclude = ('geom_cadastre',)
