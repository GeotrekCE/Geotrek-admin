# -*- encoding: utf-8 -*-

from django.contrib.gis.geos import MultiPolygon
from django.utils.translation import ugettext as _

from geotrek.common.parsers import ShapeParser
from geotrek.zoning.models import City


# Data: https://www.data.gouv.fr/fr/datasets/decoupage-administratif-communal-francais-issu-d-openstreetmap/
class CityParser(ShapeParser):
    model = City
    eid = 'code'
    fields = {
        'code': 'insee',
        'name': 'nom',
        'geom': 'geom',
    }

    def filter_code(self, src, val):
        return unicode(val)

    def filter_geom(self, src, val):
        if val is None:
            return None
        if not val.valid:
            self.add_warning(_(u"Invalid geometry for field '{src}'").format(src=src))
            return None
        if val.geom_type == 'MultiPolygon':
            return val
        elif val.geom_type == 'Polygon':
            return MultiPolygon(val)
        self.add_warning(_(u"Invalid geometry type for field '{src}'. Should be (Multi)Polygon, not {geom_type}").format(src=src, geom_type=val.geom_type))
        return None
