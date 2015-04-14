# -*- encoding: utf-8 -*-

from django.utils.translation import ugettext as _

from geotrek.common.parsers import ShapeParser, AttachmentParserMixin
from geotrek.trekking.models import Trek


class TrekParser(AttachmentParserMixin, ShapeParser):
    model = Trek
    simplify_tolerance = 2
    eid = 'name'
    constant_fields = {
        'published': True,
        'is_park_centered': False,
        'deleted': False,
    }
    natural_keys = {
        'difficulty': 'difficulty',
        'route': 'route',
        'themes': 'label',
        'practice': 'name',
        'accessibilities': 'name',
        'networks': 'network',
    }

    def filter_duration(self, src, val):
        val = val.upper().replace(',', '.')
        try:
            if u"H" in val:
                hours, minutes = val.split(u"H", 2)
                hours = float(hours.strip())
                minutes = float(minutes.strip()) if minutes.strip() else 0
                if hours < 0 or minutes < 0 or minutes >= 60:
                    raise ValueError
                return hours + minutes / 60
            else:
                hours = float(val.strip())
                if hours < 0:
                    raise ValueError
                return hours
        except ValueError:
            self.add_warning(_(u"Bad value '{val}' for field {src}. Should be like '2h30', '2,5' or '2.5'".format(val=val, src=src)))
            return None

    def filter_geom(self, src, val):
        if val is None:
            return None
        if not val.valid:
            self.add_warning(_(u"Invalid geometry for field '{src}'").format(src=src))
            return None
        if val.geom_type == 'MultiLineString':
            self.add_warning(_(u"Geometry for field '{src}' should be LineString, not MultiLineString. Unable to compute altimetry information").format(src=src))
        elif val.geom_type != 'LineString':
            self.add_warning(_(u"Invalid geometry type for field '{src}'. Should be LineString, not {geom_type}").format(src=src, geom_type=val.geom_type))
            return None
        return val
