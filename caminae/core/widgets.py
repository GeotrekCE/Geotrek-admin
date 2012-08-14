from django.conf import settings
from django.contrib.gis.geos import GEOSException, fromstr

import floppyforms as forms
from django.forms import widgets as django_widgets



def wkt_to_geom(wkt):
    try:
        geom = fromstr(wkt, srid=settings.API_SRID)
        geom.transform(settings.SRID)
        dim = 3
        extracoords = ' 0.0' * (dim - 2)  # add missing dimensions
        wkt3d = geom.wkt.replace(',', extracoords + ',')
        return wkt3d
    except (GEOSException, TypeError, ValueError):
        return None


class GeomWidget(django_widgets.TextInput):
    # hidden by default
    is_hidden = True

    def value_from_datadict(self, data, files, name):
        wkt = super(GeomWidget, self).value_from_datadict(data, files, name)
        return None if not wkt else wkt_to_geom(wkt)

    def _format_value(self, value):
        if value and not isinstance(value, basestring):
            value.transform(settings.API_SRID)
        return value


class LeafletMapWidget(forms.gis.BaseGeometryWidget):
    template_name = 'core/formfieldmap_fragment.html'
    display_wkt = settings.DEBUG

    def value_from_datadict(self, data, files, name):
        wkt = super(LeafletMapWidget, self).value_from_datadict(data, files, name)
        return None if not wkt else wkt_to_geom(wkt)

    def get_context(self, name, value, attrs=None, extra_context={}):
        context = super(LeafletMapWidget, self).get_context(name, value, attrs, extra_context)
        # Be careful, on form error, value is not a GEOSGeometry
        if value and not isinstance(value, basestring):
            value.transform(settings.API_SRID)
        context['update'] = bool(value)
        context['field'] = value
        context['fitextent'] = value is None
        return context


class MapEntityWidget(LeafletMapWidget):
    path_snapping = True
    
    def get_context(self, name, value, attrs=None, extra_context={}):
        context = super(MapEntityWidget, self).get_context(name, value, attrs, extra_context)
        context['min_snap_zoom'] = settings.MIN_SNAP_ZOOM
        context['path_snapping'] = self.path_snapping
        return context


class LineStringWidget(MapEntityWidget,
                       forms.gis.LineStringWidget):
    pass


class MultiPathWidget(MapEntityWidget):
    is_multipath = True
    
    def get_context(self, *args, **kwargs):
            context = super(MultiPathWidget, self).get_context(*args, **kwargs)
            context['is_multipath'] = self.is_multipath
            return context


class PointOrLineStringWidget(MapEntityWidget,
                             forms.gis.PointWidget,
                             forms.gis.LineStringWidget):
    geom_type = 'GEOMETRY'


class PointOrMultipathWidget(MultiPathWidget,
                             forms.gis.PointWidget):
    geom_type = 'GEOMETRY'
