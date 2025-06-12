from geotrek import settings
from geotrek.core.models import Topology


class PointTopologyParserMixin:
    def generate_topology_from_geometry(self, geometry):
        self.topology = Topology.objects.none()  # TODO: why is this needed?
        if settings.TREKKING_TOPOLOGY_ENABLED:
            serialized = f'{{"lng": {geometry.x}, "lat": {geometry.y}}}'
            self.topology = Topology.deserialize(serialized)

    def parse_obj(self, row, operation):
        super().parse_obj(row, operation)
        if settings.TREKKING_TOPOLOGY_ENABLED and self.obj.geom and self.topology:
            self.obj.mutate(self.topology)
