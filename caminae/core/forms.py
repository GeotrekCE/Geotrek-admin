from math import isnan

from django.utils.translation import ugettext_lazy as _
from django.contrib.gis.geos import LineString

import floppyforms as forms
from crispy_forms.layout import Field

from caminae.mapentity.forms import MapEntityForm
from .models import Path
from .fields import TopologyField
from .widgets import LineStringWidget


class TopologyMixinForm(MapEntityForm):
    """
    This form is a bit specific : 
    
        We use a field (topology) in order to edit the whole instance.
        Thus, at init, we load the instance into field, and at save, we
        save the field into the instance.
        
    The geom field is fully ignored, since we edit a topology.
    """
    topology = TopologyField()
    geomfields = ('topology', )

    def __init__(self, *args, **kwargs):
        super(TopologyMixinForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['topology'].initial = self.instance

    def clean(self, *args, **kwargs):
        data = super(TopologyMixinForm, self).clean()
        if 'geom' in self.errors:
            del self.errors['geom']
        return data

    def save(self, *args, **kwargs):
        topology = self.cleaned_data.pop('topology')
        instance = super(TopologyMixinForm, self).save(*args, **kwargs)
        instance.mutate(topology)
        return instance

    class Meta:
        exclude = ('offset', 'geom')


class PathForm(MapEntityForm):
    geom = forms.gis.LineStringField(widget=LineStringWidget)

    reverse_geom = forms.BooleanField(
           required=False,
           label = _("Reverse path"),
           help_text = _("The path will be reversed once saved"),
       )

    modelfields = ('name',
              'structure',
              'stake',
              'trail',
              Field('comments', css_class='input-xlarge'),
              'datasource',
              'networks',
              'usages',
              'valid')
    geomfields = ('geom',
                  'reverse_geom',)

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
