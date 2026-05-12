"""

We distinguish two types of widgets : Geometry and Topology.

Geometry widgets receive a WKT string, deserialized by GEOS.
Leaflet.Draw is used for edition.

Topology widgets receive a JSON string, deserialized by Topology.deserialize().
Geotrek custom code is used for edition.
"""

import json

from mapentity.widgets import MapWidget

from .models import Topology


class SnappedLineStringWidget(MapWidget):
    geometry_field_class = "MapEntity.GeometryField.GeometryFieldSnap"

    def serialize(self, value):
        geojson = super().serialize(value)
        snaplist = []
        if value:
            snaplist = [None for c in range(len(value.coords))]
        value = {"geom": geojson, "snap": snaplist}
        return json.dumps(value)

    def deserialize(self, value):
        if isinstance(value, str) and value:
            value = json.loads(value)
            value = value["geom"]
        return super().deserialize(value)


class BaseTopologyWidget(MapWidget):
    """A widget allowing to create topologies on a map."""

    template_name = "core/topology_widget_fragment.html"
    geometry_field_class = "MapEntity.GeometryField.TopologyField"
    is_line_topology = False
    is_point_topology = False

    def serialize(self, value):
        return value.serialize() if value else ""

    def deserialize(self, value):
        if isinstance(value, int):
            return Topology.objects.get(pk=value)
        try:
            return Topology.deserialize(value)
        except ValueError:
            return None

    def render(self, name, value, attrs=None, renderer=None):
        """Renders the fields. Parent class calls `serialize()` with the value."""
        if isinstance(value, int):
            value = Topology.objects.get(pk=value)
        attrs = attrs or {}
        attrs.update(
            is_line_topology=self.is_line_topology,
            is_point_topology=self.is_point_topology,
        )
        return super().render(name, value, attrs, renderer)


class LineTopologyWidget(BaseTopologyWidget):
    """A widget allowing to select a list of paths."""

    is_line_topology = True


class PointTopologyWidget(BaseTopologyWidget):
    """A widget allowing to point a position with a marker."""

    is_point_topology = True


class PointLineTopologyWidget(PointTopologyWidget, LineTopologyWidget):
    """A widget allowing to point a position with a marker or a list of paths."""

    pass
