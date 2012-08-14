from django.contrib.gis.geos import Point, LineString

import floppyforms as forms

from caminae.mapentity.forms import MapEntityForm
from caminae.core.widgets import PointOrMultipathWidget
from caminae.core.factories import TopologyMixinFactory, PathAggregationFactory

from .models import Infrastructure, Signage


class BaseInfrastructureForm(MapEntityForm):
    geom = forms.gis.GeometryField(widget=PointOrMultipathWidget)

    modelfields = (
            'name',
            'description',
            'type',)
    geomfields = ('geom',)

    def save(self, commit=True):
        infrastructure = super(BaseInfrastructureForm, self).save(commit=False)
        # TODO: this is completely wrong, but we have no topology editor
        topo_object = TopologyMixinFactory.create()
        infrastructure.topo_object = topo_object
        infrastructure.date_insert = topo_object.date_insert
        infrastructure.date_update = topo_object.date_update
        infrastructure.delete = topo_object.delete
        infrastructure.kind = topo_object.kind
        infrastructure.geom = LineString(Point(0,0,0), Point(1,1,0))
        infrastructure.offset = topo_object.offset
        if commit:
            infrastructure.save()
        PathAggregationFactory.create(topo_object=infrastructure)
        return infrastructure


class InfrastructureForm(BaseInfrastructureForm):
    class Meta:
        model = Infrastructure
        exclude = ('deleted', 'kind', 'troncons', 'offset')  # TODO: topology editor


class SignageForm(BaseInfrastructureForm):
    class Meta:
        model = Signage
        exclude = ('deleted', 'kind', 'troncons', 'offset')
