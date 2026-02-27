from django.utils.translation import gettext as _
from vectortiles import VectorLayer

from geotrek.core.models import Path


class PathVectorLayer(VectorLayer):
    model = Path
    id = "path"  # id for data layer in vector tile
    tile_fields = ("name", "id")

    def get_queryset(self):
        """Hide all ``Path`` records that are not marked as visible."""
        qs = Path.objects.filter(visible=True)
        qs = qs.extra(
            select={
                "name": "CASE WHEN name IS NULL OR name = '' THEN CONCAT(%s || ' ' || id) ELSE name END"
            },
            select_params=(_("path"),),
        )
        return qs
