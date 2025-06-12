from django.utils.translation import gettext as _
from geotrek import settings
from geotrek.common.parsers import GlobalImportError, RowImportError
from geotrek.core.models import Path, Topology


class PointTopologyParserMixin:
    topology = Topology.objects.none()  # TODO: why is this needed?

    def start(self):
        if settings.TREKKING_TOPOLOGY_ENABLED and not Path.objects.exists():
            raise GlobalImportError(
                _("You need to add a path network before importing %(model)s objects") % {"model": self.model}
            )
        super().start()

    def generate_topology_from_geometry(self, geometry):
        if geometry.geom_type != "Point":
            raise RowImportError(
                _(
                    "Invalid geometry type: should be 'Point', not '{geom_type}'"
                ).format(geom_type=geometry.geom_type)
            )
        self.topology = Topology.objects.none()  # TODO: why is this needed?
        if settings.TREKKING_TOPOLOGY_ENABLED:
            # Use existing topology helpers to transform a Point(x, y)
            # to a path aggregation (topology)
            serialized = f'{{"lng": {geometry.x}, "lat": {geometry.y}}}'
            self.topology = Topology.deserialize(serialized)
            # Move deserialization aggregations to the object

    def parse_obj(self, row, operation):
        super().parse_obj(row, operation)
        if settings.TREKKING_TOPOLOGY_ENABLED and self.obj.geom and self.topology:
            self.obj.mutate(self.topology)
