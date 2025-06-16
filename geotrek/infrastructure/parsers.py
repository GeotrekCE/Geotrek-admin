from django.contrib.gis.geos import Point

from geotrek.common.parsers import GeotrekParser, OpenStreetMapParser
from geotrek.core.mixins.parsers import PointTopologyParserMixin
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


class OpenStreetMapInfrastructureParser(PointTopologyParserMixin, OpenStreetMapParser):
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.type:
            self.constant_fields["type"] = self.type

    def build_geos_geometry(self, src, val):
        type, lng, lat, area, bbox = val
        geom = None
        if type == "node":
            geom = Point(float(lng), float(lat), srid=self.osm_srid)  # WGS84
        elif type == "way":
            geom = self.get_centroid_from_way(area)
        elif type == "relation":
            geom = self.get_centroid_from_relation(bbox)
        return geom
