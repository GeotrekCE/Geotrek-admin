import json

from django.conf import settings
from django.contrib.gis.geos import GEOSGeometry, MultiPolygon, Polygon, fromstr
from django.utils.translation import gettext as _

from geotrek.common.parsers import (
    DownloadImportError,
    GeotrekParser,
    GlobalImportError,
    OpenStreetMapParser,
    RowImportError,
    ShapeParser,
)
from geotrek.common.utils.parsers import force_geom_to_2d
from geotrek.zoning.models import (
    City,
    District,
    RestrictedArea,
    VigilanceArea,
)


# Data: https://www.data.gouv.fr/fr/datasets/decoupage-administratif-communal-francais-issu-d-openstreetmap/
class CityParser(ShapeParser):
    model = City
    eid = "code"
    label = "Cities"
    label_fr = "Communes"
    fields = {
        "code": "insee",
        "name": "nom",
        "geom": "geom",
    }
    m2m_fields = {}

    def filter_code(self, src, val):
        return str(val)

    def filter_geom(self, src, val):
        if val is None:
            return None
        if not val.valid:
            self.add_warning(_("Invalid geometry for field '{src}'").format(src=src))
            return None
        if val.geom_type == "MultiPolygon":
            return val
        elif val.geom_type == "Polygon":
            return MultiPolygon(val)
        raise GlobalImportError(
            _(
                "Invalid geometry type for field '{src}'. "
                "Should be (Multi)Polygon, not {geom_type}"
            ).format(src=src, geom_type=val.geom_type)
        )


class OpenStreetMapZoningParserMixin(OpenStreetMapParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.query_settings.osm_element_type = "relation"
        self.query_settings.output = "tags"

    def filter_geom(self, src, val):
        element_type, id = val

        osm_id = element_type[0].upper() + str(id)

        params = {
            "osm_ids": osm_id,
            "polygon_text": 1,
            "format": "json",
            "polygon_threshold": 0.0001,
        }
        try:
            response = self.request_or_retry(self.url_nominatim, params=params)
            root = response.json()[0]

            wkt = root["geotext"]

            geom = fromstr(wkt, srid=self.osm_srid)
            geom.srid = self.osm_srid
            geom.transform(settings.SRID)

            if isinstance(geom, Polygon):
                geom = MultiPolygon(geom)

            return geom
        except DownloadImportError as e:
            raise RowImportError(str(e))


class OpenStreetMapDistrictParser(OpenStreetMapZoningParserMixin):
    """Parser to import district from OpenStreetMap"""

    model = District
    fields = {
        "name": "tags.name",
        "geom": ("type", "id"),
    }
    constant_fields = {
        "published": True,
    }


class OpenStreetMapRestrictedAreaParser(OpenStreetMapZoningParserMixin):
    """Parser to import restricted areas from OpenStreetMap"""

    area_type = None
    model = RestrictedArea
    fields = {
        "name": "tags.name",
        "geom": ("type", "id"),
    }
    constant_fields = {
        "published": True,
    }
    natural_keys = {"area_type": "name"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.area_type:
            self.constant_fields["area_type"] = self.area_type


class OpenStreetMapCityParser(OpenStreetMapZoningParserMixin):
    """Parser to import cities from OpenStreetMap"""

    model = City
    fields = {
        "name": "tags.name",
        "geom": ("type", "id"),
    }
    constant_fields = {
        "published": True,
    }
    code_tag = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.code_tag:
            self.fields["code"] = f"tags.{self.code_tag}"


class VigilanceAreaParser:
    model = VigilanceArea
    eid = "eid"
    fields = {"name": "nom", "geom": "geom", "eid": "id"}
    m2m_fields = {}
    constant_fields = {
        "published": True,
    }
    natural_keys = {"vigilance_area_type": "name"}

    def filter_code(self, src, val):
        return str(val)

    def filter_geom(self, src, val):
        if val is None:
            return None
        if not val.valid:
            self.add_warning(_("Invalid geometry for field '{src}'").format(src=src))
            return None
        if val.geom_type == "MultiPolygon":
            return val
        elif val.geom_type == "Polygon":
            return MultiPolygon(val)
        raise GlobalImportError(
            _(
                "Invalid geometry type for field '{src}'. "
                "Should be (Multi)Polygon, not {geom_type}"
            ).format(src=src, geom_type=val.geom_type)
        )


class GeotrekVigilanceAreaParser(GeotrekParser):
    """Geotrek parser for Geotrek vigilance areas"""

    fill_empty_translated_fields = True
    url = None
    model = VigilanceArea
    replace_fields = {"eid": "uuid", "geom": "geometry"}
    url_categories = {
        "structure": "structure",
        "sources": "source",
        "vigilance_area_type": "vigilancearea_type",
    }
    categories_keys_api_v2 = {
        "structure": "name",
        "sources": "name",
        "vigilance_area_type": "name",
    }
    natural_keys = {
        "structure": "name",
        "sources": "name",
        "vigilance_area_type": "name",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop("uuid")  # TEST
        self.next_url = f"{self.url}/api/v2/vigilancearea"

    def build_geos_geometry(self, src, val):
        geom = GEOSGeometry(json.dumps(val))
        geom = force_geom_to_2d(geom)
        return geom
