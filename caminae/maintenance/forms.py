from django.contrib.gis.geos import Point

import floppyforms as forms
from crispy_forms.layout import Field

from caminae.core.models import Path
from caminae.core.factories import PathFactory, TopologyMixinFactory, PathAggregationFactory
from caminae.core.forms import MapEntityForm
from caminae.core.widgets import PointOrLineStringWidget

from .models import Intervention


class InterventionForm(MapEntityForm):
    geom = forms.gis.GeometryField(widget=PointOrLineStringWidget)

    modelfields = (
            'name',
            'structure',
            'date',
            'status',
            'typology',
            'disorders',
            Field('comments', css_class='input-xlarge'),
            'in_maintenance',
            'length',
            'height',
            'width',
            'area',
            'slope',
            'material_cost',
            'heliport_cost',
            'subcontract_cost',
            'stake',
            'project',)
    geomfields = ('geom',)

    def save(self, commit=True):
        intervention = super(InterventionForm, self).save(commit=False)
        if not commit:
            return intervention
        
        geom = self.cleaned_data.get('geom')
        if not geom:
            pass # raise ValueError !

        if isinstance(geom, Point):
            closest_paths = Path.objects.distance(geom).order_by('-distance')
            if not closest_paths:
                closest_paths = [PathFactory.create()]
                # TODO: raise not possible without path !

            # TODO
            path = closest_paths[0]
            distance = 0
            position = position = 0.5
            
            topology = TopologyMixinFactory.create(offset=distance)
            PathAggregationFactory.create(topo_object=topology,
                                          path=path,
                                          start_position=position,
                                          end_position=position)
            intervention.save()
            intervention.topologies.add(topology)
        else:
            # TODO: transform list of paths to TopologyMixin
            pass
        return intervention

    class Meta:
        model = Intervention
        exclude = ('deleted', 'topologies', 'jobs') # TODO
