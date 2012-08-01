from django.conf import settings
from django.contrib.gis.geos import fromstr

import floppyforms as forms


class BaseMapWidget(forms.gis.BaseGeometryWidget):
    map_srid = 4326
    template_name = 'floppyforms/gis/openlayers.html'
    display_wkt = True

    def value_from_datadict(self, data, files, name):
        wkt = super(BaseMapWidget, self).value_from_datadict(data, files, name)
        # TODO : map is 4326, data is 2154 - Remove this when leaflet ready for proj
        geom = fromstr(wkt)
        geom.transform(settings.SRID)
        wkt3d = geom.wkt.replace(',', ' 0.0,')  # TODO: woot!
        return wkt3d

    class Media:
        js = (
            'http://openlayers.org/api/2.10/OpenLayers.js',
            'floppyforms/js/MapWidget.js',
        )


class LineStringWidget(BaseMapWidget,
                       forms.gis.LineStringWidget):
    pass
