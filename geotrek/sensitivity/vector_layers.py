from vectortiles import VectorLayer

from geotrek.sensitivity.helpers import annotate_display_geom
from geotrek.sensitivity.models import SensitiveArea


class SensitivityVectorLayer(VectorLayer):
    model = SensitiveArea
    id = f"{SensitiveArea.__name__.lower()}"  # id for data layer in vector tile
    geom_field = "geom_display"  # geom field to consider in qs
    tile_fields = ("id",)

    def get_queryset(self):
        return annotate_display_geom(
            SensitiveArea.objects.existing().select_related("species"),
            field_name="geom_display",
        )
