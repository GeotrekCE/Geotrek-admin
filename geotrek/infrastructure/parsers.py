from django.conf import settings
from django.contrib.gis.geos import Point
from django.utils.translation import gettext as _

from geotrek.common.parsers import GeotrekParser, GlobalImportError, OpenStreetMapParser
from geotrek.core.models import Path, Topology
from geotrek.infrastructure.models import Infrastructure


class GeotrekInfrastructureParser(GeotrekParser):
    """Geotrek parser for Infrastructure"""

    fill_empty_translated_fields = True
    url = None
    model = Infrastructure
    constant_fields = {"deleted": False}
    replace_fields = {"eid": "uuid", "geom": "geometry"}
    url_categories = {
        "structure": "structure",
        "condition": "infrastructure_condition",
        "type": "infrastructure_type",
    }
    categories_keys_api_v2 = {
        "structure": "name",
        "condition": "label",
        "type": "label",
    }
    natural_keys = {"structure": "name", "condition": "label", "type": "label"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.next_url = f"{self.url}/api/v2/infrastructure"


class OpenStreetMapInfrastructureParser(OpenStreetMapParser):
    """Parser to import infrastructures from OpenStreetMap"""

    type = None
    model = Infrastructure
    fields = {
        "eid": ("type", "id"),  # ids are unique only for object of the same type
        "name": "tags.name",
        "geom": ("type", "lon", "lat", "geometry", "bounds"),
        "description": "tags.description",
    }
    constant_fields = {"published": True}
    natural_keys = {
        "type": "label",
    }
    non_fields = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.type:
            self.constant_fields["type"] = self.type

    def start(self):
        super().start()
        if settings.TREKKING_TOPOLOGY_ENABLED and not Path.objects.exists():
            raise GlobalImportError(
                _("You need to add a network of paths before importing Infrastructures")
            )

    def filter_geom(self, src, val):
        # convert OSM geometry to point
        type, lng, lat, area, bbox = val
        original_geom = None
        projected_geom = None
        if type == "node":
            original_geom = Point(float(lng), float(lat), srid=self.osm_srid)  # WGS84
            projected_geom = original_geom.transform(settings.SRID, clone=True)
        elif type == "way":
            original_geom, projected_geom = self.get_centroid_from_way(area)
        elif type == "relation":
            original_geom, projected_geom = self.get_centroid_from_relation(bbox)

        # create topology
        self.topology = None
        if settings.TREKKING_TOPOLOGY_ENABLED:
            # Use existing topology helpers to transform a Point(x, y)
            # to a path aggregation (topology)
            serialized = f'{{"lng": {original_geom.x}, "lat": {original_geom.y}}}'
            self.topology = Topology.deserialize(serialized)
            # Move deserialization aggregations to the POI
        return projected_geom

    def parse_obj(self, row, operation):
        super().parse_obj(row, operation)
        if settings.TREKKING_TOPOLOGY_ENABLED and self.obj.geom and self.topology:
            self.obj.mutate(self.topology)
