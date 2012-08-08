from django.conf import settings
from django.contrib.gis.geos import GEOSException, fromstr

import floppyforms as forms


class LeafletMapWidget(forms.gis.BaseGeometryWidget):
    map_srid = settings.MAP_SRID
    template_name = 'core/formfieldmap_fragment.html'
    display_wkt = settings.DEBUG

    def value_from_datadict(self, data, files, name):
        wkt = super(LeafletMapWidget, self).value_from_datadict(data, files, name)
        if not wkt:
            return None
        try:
            geom = fromstr(wkt, srid=self.map_srid)
            geom.transform(settings.SRID)
            dim = 3
            extracoords = ' 0.0' * (dim - 2)  # add missing dimensions
            wkt3d = geom.wkt.replace(',', extracoords + ',')
            return wkt3d
        except (GEOSException, TypeError, ValueError):
            return None

    def get_context(self, name, value, attrs=None, extra_context={}):
        context = super(LeafletMapWidget, self).get_context(name, value, attrs, extra_context)
        # Be careful, on form error, value is not a GEOSGeometry
        if value and not isinstance(value, basestring):
            value.transform(self.map_srid)
        context['update'] = bool(value)
        context['field'] = value
        context['fitextent'] = value is None
        return context


class MapEntityWidget(LeafletMapWidget):
    path_snapping = True


class LineStringWidget(MapEntityWidget,
                       forms.gis.LineStringWidget):
    pass


class PointOrLineStringWidget(MapEntityWidget,
                             forms.gis.PointWidget,
                             forms.gis.LineStringWidget):
    geom_type = 'GEOMETRY'
