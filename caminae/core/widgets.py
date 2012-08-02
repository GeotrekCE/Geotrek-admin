from django.conf import settings
from django.contrib.gis.geos import fromstr

import floppyforms as forms


class BaseMapWidget(forms.gis.BaseGeometryWidget):
    map_srid = 4326
    template_name = 'core/formfieldmap_fragment.html'

    def value_from_datadict(self, data, files, name):
        wkt = super(BaseMapWidget, self).value_from_datadict(data, files, name)
        geom = fromstr(wkt, srid=self.map_srid)
        geom.transform(settings.SRID)
        dim = 3
        extracoords = ' 0.0' * (dim - 2)  # add missing dimensions
        wkt3d = geom.wkt.replace(',', extracoords + ',')
        return wkt3d

    def get_context(self, name, value, attrs=None, extra_context={}):
        context = super(BaseMapWidget, self).get_context(name, value, attrs, extra_context)
        # Be careful, on form error, value is not a GEOSGeometry
        if value and not isinstance(value, basestring):
            value.transform(self.map_srid)
        context['field'] = value
        return context


class LineStringWidget(BaseMapWidget,
                       forms.gis.LineStringWidget):
    pass
