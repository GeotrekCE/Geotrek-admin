from django.conf import settings
import floppyforms as forms

from caminae.common.utils import wkt_to_geom


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


class PointWidget(MapEntityWidget,
                       forms.gis.PointWidget):
    pass


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
