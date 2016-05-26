# -*- encoding: utf-8 -*-

from django.contrib.gis.geos import Point
from django.utils.translation import ugettext as _

from geotrek.common.parsers import ShapeParser, AttachmentParserMixin
from geotrek.trekking.models import Trek


class DurationParserMixin(object):
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
        except (TypeError, ValueError):
            self.add_warning(_(u"Bad value '{val}' for field {src}. Should be like '2h30', '2,5' or '2.5'".format(val=val, src=src)))
            return None


class TrekParser(DurationParserMixin, AttachmentParserMixin, ShapeParser):
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

    def filter_geom(self, src, val):
        if val is None:
            return None
        if val.geom_type == 'MultiLineString':
            points = val[0]
            for i, path in enumerate(val[1:]):
                distance = Point(points[-1]).distance(Point(path[0]))
                if distance > 5:
                    self.add_warning(_(u"Not contiguous segment {i} ({distance} m) for geometry for field '{src}'").format(i=i + 2, p1=points[-1], p2=path[0], distance=int(distance), src=src))
                points += path
            return points
        elif val.geom_type != 'LineString':
            self.add_warning(_(u"Invalid geometry type for field '{src}'. Should be LineString, not {geom_type}").format(src=src, geom_type=val.geom_type))
            return None
        return val
