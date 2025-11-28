from django.contrib.gis.geos import GEOSGeometry, Point
from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import gettext as _

from geotrek.common.parsers import GeotrekParser, OpenStreetMapParser
from geotrek.core.mixins.parsers import PointTopologyParserMixin
from geotrek.infrastructure.models import Infrastructure
from geotrek.trekking.parsers import ApidaeBaseParser


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


class ApidaeInfrastructureParser(PointTopologyParserMixin, ApidaeBaseParser):
    model = Infrastructure
    eid = "eid"
    separator = None
    infrastructure_type = None

    responseFields = [
        "id",
        "localisation.geolocalisation.geoJson",
        "nom",
        "presentation",
        "prestations.tourismesAdaptes",
    ]
    fields = {
        "eid": "id",
        "geom": "localisation.geolocalisation.geoJson",
        "name": "nom.libelleFr",
        "description": (
            "presentation.descriptifCourt.libelleFr",
            "presentation.descriptifDetaille.libelleFr",
        ),
        "accessibility": "prestations.tourismesAdaptes",
    }
    natural_keys = {
        "type": "label",
    }
    field_options = {
        "type": {"create": True},
        "name": {"required": True},
        "geom": {"required": True},
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.infrastructure_type:
            self.constant_fields = self.constant_fields.copy()
            self.constant_fields["type"] = self.infrastructure_type
        else:
            msg = _(
                "An infrastructure type must be specified in the parser configuration."
            )
            raise ImproperlyConfigured(msg)

    def build_geos_geometry(self, src, val):
        return GEOSGeometry(str(val))

    def filter_description(self, src, val):
        short_descr, detailed_descr = val
        return detailed_descr or short_descr

    def filter_accessibility(self, src, val):
        accessibilities = [a.get("libelleFr") for a in val]
        return "\n".join(accessibilities)


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
