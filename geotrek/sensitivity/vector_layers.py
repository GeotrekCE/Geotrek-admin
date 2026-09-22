from vectortiles import VectorLayer

from geotrek.sensitivity.models import SensitiveArea


class SensitivityVectorLayer(VectorLayer):
    model = SensitiveArea
    id = f"{SensitiveArea.__name__.lower()}"  # id for data layer in vector tile
    geom_field = SensitiveArea.main_geom_field  # geom field to consider in qs
    tile_fields = ("id",)
