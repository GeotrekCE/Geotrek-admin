from vectortiles import VectorLayer

from geotrek.core.models import Path


class PathVectorLayer(VectorLayer):
    model = Path
    id = "path"  # id for data layer in vector tile
    tile_fields = ("name", "id")

    def get_vector_tile_queryset(self, z, x, y):
        qs = super().get_vector_tile_queryset(z, x, y)
        qs.filter(draft=False)
        return qs
