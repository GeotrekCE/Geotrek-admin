from djgeojson.views import GeoJSONLayerView

from .models import Path


class PathList(GeoJSONLayerView):
    model = Path
    fields = ('name', 'valid',)
