from django.utils.translation import ugettext_lazy as _

import floppyforms as forms

from caminae.common.forms import CommonForm
from .models import Path
from .fields import TopologyField
from .widgets import SnappedLineStringWidget


class TopologyForm(CommonForm):
    """
    This form is a bit specific : 
    
        We use a field (topology) in order to edit the whole instance.
        Thus, at init, we load the instance into field, and at save, we
        save the field into the instance.
        
    The geom field is fully ignored, since we edit a topology.
    """
    topology = TopologyField(label="")
    geomfields = ('topology', )

    def __init__(self, *args, **kwargs):
        super(TopologyForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['topology'].initial = self.instance

    def clean(self, *args, **kwargs):
        data = super(TopologyForm, self).clean()
        if 'geom' in self.errors:
            del self.errors['geom']
        return data

    def save(self, *args, **kwargs):
        topology = self.cleaned_data.pop('topology')
        instance = super(TopologyForm, self).save(*args, **kwargs)
        instance.mutate(topology)
        return instance

    class Meta:
        exclude = ('offset', 'geom')


class PathForm(CommonForm):
    geom = forms.gis.LineStringField(widget=SnappedLineStringWidget)

    reverse_geom = forms.BooleanField(
           required=False,
           label = _("Reverse path"),
           help_text = _("The path will be reversed once saved"),
       )

    modelfields = ('name',
              'stake',
              'comfort',
              'trail',
              'departure',
              'arrival',
              'comments',
              'datasource',
              'networks',
              'usages',
              'valid')
    geomfields = ('geom',
                  'reverse_geom',)

    def clean_geom(self):
        data = self.cleaned_data['geom']
        if not data.simple:
            raise forms.ValidationError("Geometry is not simple.")
        if not Path.disjoint(data, self.cleaned_data.get('pk', '-1')):
            raise forms.ValidationError("Geometry overlaps another.")
        return data

    def save(self, commit=True):
        path = super(PathForm, self).save(commit=False)

        if self.cleaned_data.get('reverse_geom'):
            path.reverse()

        if commit:
            path.save()
            self.save_m2m()

        return path

    class Meta:
        model = Path
        exclude = ('geom_cadastre',)
