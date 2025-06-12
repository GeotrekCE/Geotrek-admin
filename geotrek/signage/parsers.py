from django.conf import settings
from django.contrib.gis.geos import Point
from django.utils.translation import gettext as _

from geotrek.common.parsers import (
    GeotrekParser,
    GlobalImportError,
    OpenStreetMapParser,
)
from geotrek.core.mixins.parsers import PointTopologyParserMixin
from geotrek.core.models import Path, Topology
from geotrek.signage.models import Signage


class GeotrekSignageParser(GeotrekParser):
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

    def filter_geom(self, src, val):
        # convert OSM geometry to point
        lng, lat = val
        geom = Point(float(lng), float(lat), srid=self.osm_srid)  # WGS84
        self.generate_topology_from_geometry(geom)
        geom.transform(settings.SRID)
        return geom
