"""

    We distinguish two types of widgets : Geometry and Topology.

    Geometry widgets receive a WKT string, deserialized by GEOS.
    Leaflet.Draw is used for edition.

    Topology widgets receive a JSON string, deserialized by Topology.deserialize().
    Geotrek custom code is used for edition.

    :notes:

        The purpose of floppyforms is to use Django templates for widget rendering.

"""
import json

from django.template import loader
from django.utils import six

import floppyforms as forms
from mapentity.widgets import MapWidget

from .models import Topology


class SnappedLineStringWidget(MapWidget):
    geometry_field_class = 'MapEntity.GeometryField.GeometryFieldSnap'

    def serialize(self, value):
        geojson = super(SnappedLineStringWidget, self).serialize(value)
        value = {'geom': geojson}
        return json.dumps(value)

    def deserialize(self, value):
        value = json.loads(value)
        value = value['geom']
        value = json.dumps(value)
        return super(SnappedLineStringWidget, self).deserialize(value)


class BaseTopologyWidget(forms.Textarea):
    """ A widget allowing to create topologies on a map.
    """
    template_name = 'core/fieldtopology_fragment.html'
    display_json = settings.DEBUG
    is_multipath = False
    is_point = False

    def value_from_datadict(self, data, files, name):
        return data.get(name)

    def get_context(self, name, value, *args, **kwargs):
        topologyjson = ''
        if value:
            if isinstance(value, basestring):
                topologyjson = value
            else:
                if isinstance(value, int):
                    value = Topology.objects.get(pk=value)
                topologyjson = value.serialize()
        context = super(BaseTopologyWidget, self).get_context(name, topologyjson, *args, **kwargs)
        context['module'] = 'map_%s' % name.replace('-', '_')
        context['callback'] = context['module'] + 'Init'
        context['display_wkt'] = self.display_json   # called wkt because inherit field geometry
        context['is_multipath'] = self.is_multipath
        context['is_point'] = self.is_point
        context['update'] = bool(value)
        context['topology'] = value
        context['topologyjson'] = topologyjson
        context['path_snapping'] = True
        return context


class LineTopologyWidget(BaseTopologyWidget):
    """ A widget allowing to select a list of paths.
    """
    is_multipath = True


class PointTopologyWidget(BaseTopologyWidget):
    """ A widget allowing to point a position with a marker.
    """
    is_point = True


class PointLineTopologyWidget(PointTopologyWidget, LineTopologyWidget):
    """ A widget allowing to point a position with a marker or a list of paths.
    """
    pass


class TopologyReadonlyWidget(BaseTopologyWidget):
    template_name = 'core/fieldtopologyreadonly_fragment.html'

    def get_context(self, *args, **kwargs):
        context = super(TopologyReadonlyWidget, self).get_context(*args, **kwargs)
        topology = context['topology']
        if topology and not isinstance(topology, basestring):
            context['object'] = topology.geom
        context['mapname'] = context['module']
        return context
