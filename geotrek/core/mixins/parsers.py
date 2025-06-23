from abc import ABC, abstractmethod

from django.utils.translation import gettext as _

from geotrek import settings
from geotrek.common.parsers import GlobalImportError, RowImportError
from geotrek.core.models import Path, Topology


class PointTopologyParserMixin(ABC):
    def start(self):
        if settings.TREKKING_TOPOLOGY_ENABLED and not Path.objects.exists():
            raise GlobalImportError(
                _(
                    "You need to add a network of paths before importing '%(model)s' objects"
                )
                % {"model": self.model.__name__}
            )
        super().start()

    @abstractmethod
    def build_geos_geometry(self, src, val):
        """
        Should be implemented by the subclass to convert source data into the GEOSGeometry that will be used in the filter_geom method.
        """

    def generate_topology_from_geometry(self, geometry):
        if geometry.geom_type != "Point":
            raise RowImportError(
                _("Invalid geometry type: should be 'Point', not '{geom_type}'").format(
                    geom_type=geometry.geom_type
                )
            )
        if settings.TREKKING_TOPOLOGY_ENABLED:
            # Use existing topology helpers to transform a Point(x, y)
            # to a path aggregation (topology)
            serialized = f'{{"lng": {geometry.x}, "lat": {geometry.y}}}'
            self.topology = Topology.deserialize(serialized)
            # Move deserialization aggregations to the object

    def filter_geom(self, src, val):
        if val is None:
            raise RowImportError(_("Cannot import object: geometry is None"))
        try:
            if hasattr(super(), "filter_geom"):
                super().filter_geom(src, val)
            geom = self.build_geos_geometry(src, val)
        except Exception:
            raise RowImportError(
                _("Could not parse geometry from value '{value}'").format(value=val)
            )
        self.generate_topology_from_geometry(geom)
        geom.transform(settings.SRID)
        return geom

    def parse_obj(self, row, operation):
        super().parse_obj(row, operation)
        if settings.TREKKING_TOPOLOGY_ENABLED and self.obj.geom and self.topology:
            self.obj.mutate(self.topology)
