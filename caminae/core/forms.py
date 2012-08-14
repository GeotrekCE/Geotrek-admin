from math import isnan

from django.contrib.gis.geos import LineString, Point
from django.utils.translation import ugettext_lazy as _

import floppyforms as forms
from crispy_forms.layout import Field

from caminae.mapentity.forms import MapEntityForm

from .models import Path
from .widgets import LineStringWidget
from .factories import TopologyMixinFactory, PathAggregationFactory


class TopologyMixinForm(MapEntityForm):
    def save(self, commit=True, **kwargs):
        obj = super(TopologyMixinForm, self).save(commit=False, **kwargs)
        # TODO: this is completely wrong, but we have no topology editor yet
        topo_object = TopologyMixinFactory.create()
        obj.topo_object = topo_object
        obj.date_insert = topo_object.date_insert
        obj.date_update = topo_object.date_update
        obj.delete = topo_object.delete
        obj.kind = topo_object.kind
        obj.geom = LineString(Point(0,0,0), Point(1,1,0))
        obj.offset = topo_object.offset
        if commit:
            obj.save()
        PathAggregationFactory.create(topo_object=obj)
        return obj


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
