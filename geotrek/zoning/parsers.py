from django.conf import settings
from django.contrib.gis.geos import MultiPolygon, Polygon, fromstr
from django.utils.translation import gettext as _

from geotrek.common.parsers import (
    DownloadImportError,
    GlobalImportError,
    OpenStreetMapParser,
    RowImportError,
    ShapeParser,
)
from geotrek.zoning.models import City, District, RestrictedArea


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
