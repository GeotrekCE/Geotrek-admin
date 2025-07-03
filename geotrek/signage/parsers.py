import json

from django.contrib.gis.geos import GEOSGeometry, Point

from geotrek.common.parsers import (
    GeotrekParser,
    OpenStreetMapParser,
)
from geotrek.common.utils.parsers import force_geom_to_2d
from geotrek.core.mixins.parsers import PointTopologyParserMixin
from geotrek.core.models import Topology
from geotrek.signage.models import Signage


class GeotrekSignageParser(PointTopologyParserMixin, GeotrekParser):
    """Geotrek parser for Signage"""

    fill_empty_translated_fields = True
    url = None
    model = Signage
    constant_fields = {"deleted": False}
    replace_fields = {"eid": "uuid", "geom": "geometry"}
    url_categories = {
        "structure": "structure",
        "sealing": "signage_sealing",
        "conditions": "signage_condition",
        "type": "signage_type",
    }
    categories_keys_api_v2 = {
        "structure": "name",
        "conditions": "label",
        "sealing": "label",
        "type": "label",
    }
    natural_keys = {
        "structure": "name",
        "conditions": "label",
        "sealing": "label",
        "type": "label",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.next_url = f"{self.url}/api/v2/signage"

    def build_geos_geometry(self, src, val):
        geom = GEOSGeometry(json.dumps(val))
        geom = force_geom_to_2d(geom)
        return geom


class OpenStreetMapSignageParser(PointTopologyParserMixin, OpenStreetMapParser):
    """Parser to import signage from OpenStreetMap"""

    type = None
    model = Signage
    eid = "eid"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.query_settings.osm_element_type = "node"

        if self.type:
            self.constant_fields["type"] = self.type

    fields = {
        "eid": ("type", "id"),  # ids are unique only among objects of the same type
        "name": "tags.name",
        "description": "tags.description",
        "geom": ("lon", "lat"),
    }
    constant_fields = {
        "published": True,
    }
    natural_keys = {
        "type": "label",
    }
    field_options = {"geom": {"required": True}, "type": {"required": True}}
    topology = Topology.objects.none()

    def build_geos_geometry(self, src, val):
        # convert OSM geometry to point
        lng, lat = val
        return Point(float(lng), float(lat), srid=self.osm_srid)
