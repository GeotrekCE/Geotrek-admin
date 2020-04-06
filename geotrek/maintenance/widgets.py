from mapentity.widgets import LeafletWidget

from .models import Topology


class InterventionWidget(LeafletWidget):
    """ A widget allowing to create topologies on a map.
    """
    is_point_topology = True

    def serialize(self, value):
        if value:
            return value.geom.transform(4326, clone=True).geojson

    def render(self, name, value, attrs=None, renderer=None):
        """Renders the fields. Parent class calls `serialize()` with the value.
        """
        if isinstance(value, int):
            value = Topology.objects.get(pk=value)
        attrs = attrs or {}
        attrs.update(is_point_topology=self.is_point_topology)
        return super(InterventionWidget, self).render(name, value, attrs, renderer)
