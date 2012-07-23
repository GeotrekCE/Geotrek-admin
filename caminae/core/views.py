from djgeojson.views import GeoJSONLayerView

from .models import Path


class PathList(GeoJSONLayerView):
    model = Path
    fields = ('name', 'valid',)
    precision = 2
    # srid = 4326
    # simplify = 0.5
