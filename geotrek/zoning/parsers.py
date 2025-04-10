from django.contrib.gis.geos import MultiPolygon
from django.utils.translation import gettext as _

from geotrek.common.parsers import GlobalImportError, ShapeParser
from geotrek.zoning.models import City


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
