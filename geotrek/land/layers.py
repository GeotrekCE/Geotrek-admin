from django.conf import settings
from django.core.cache import cache
from django.db.models import Case, CharField, F, Value, When
from vectortiles import VectorLayer

from . import models


class EdgeVectorLayerMixin:
    """Mixin factorizing common logic for edge vector layers.

    Subclasses must define:
        - ``model``: the Django model class
        - ``type_related_name``: the related field name (e.g. ``"physical_type"``)
        - ``type_value_field``: the lookup for the display name (e.g. ``"physical_type__name"``)
        - ``style_key``: the key used in ``COLORS_POOL`` and ``MAP_STYLES``
    """

    model = None
    type_related_name = None
    type_value_field = None
    style_key = None

    def get_color_by_type(self):
        color_by_type_cache_key = f"{self.style_key}_color_by_type"
        color_by_type = cache.get(color_by_type_cache_key, {})

        if not color_by_type:
            color_pools = getattr(settings, "COLORS_POOL", {})
            colors = color_pools.get(self.style_key, [])
            types = (
                self.model.objects.existing()
                .select_related(self.type_related_name)
                .values_list(self.type_value_field, flat=True)
                .order_by(self.type_value_field)
                .distinct()
            )
            color_by_type = {
                name: colors[i % len(colors)] for i, name in enumerate(types) if colors
            }
            cache.set(color_by_type_cache_key, color_by_type, None)

        whens = [
            When(
                **{self.type_value_field: name},
                then=Value(color),
            )
            for name, color in color_by_type.items()
            if color_by_type
        ]
        return whens

    def get_queryset(self):
        color_by_type = self.get_color_by_type()
        default_color = settings.MAPENTITY_CONFIG["MAP_STYLES"][self.style_key][
            "default_color"
        ]
        return (
            self.model.objects.existing()
            .select_related(self.type_related_name)
            .annotate(name=F(self.type_value_field))
            .annotate(
                color=Case(
                    *color_by_type,
                    default=Value(default_color),
                    output_field=CharField(),
                )
                if color_by_type
                else Value(default_color)
            )
        )


class PhysicalEdgeVectorLayer(EdgeVectorLayerMixin, VectorLayer):
    model = models.PhysicalEdge
    id = f"{models.PhysicalEdge.__name__.lower()}"
    geom_field = models.PhysicalEdge.main_geom_field
    tile_fields = ("id", "name", "color")
    type_related_name = "physical_type"
    type_value_field = "physical_type__name"
    style_key = "physicaledge"


class LandEdgeVectorLayer(EdgeVectorLayerMixin, VectorLayer):
    model = models.LandEdge
    id = f"{models.LandEdge.__name__.lower()}"
    geom_field = models.LandEdge.main_geom_field
    tile_fields = ("id", "name", "color")
    type_related_name = "land_type"
    type_value_field = "land_type__name"
    style_key = "landedge"


class CirculationEdgeVectorLayer(EdgeVectorLayerMixin, VectorLayer):
    model = models.CirculationEdge
    id = f"{models.CirculationEdge.__name__.lower()}"
    geom_field = models.CirculationEdge.main_geom_field
    tile_fields = ("id", "name", "color")
    type_related_name = "circulation_type"
    type_value_field = "circulation_type__name"
    style_key = "circulationedge"


class CompetenceEdgeVectorLayer(EdgeVectorLayerMixin, VectorLayer):
    model = models.CompetenceEdge
    id = f"{models.CompetenceEdge.__name__.lower()}"
    geom_field = models.CompetenceEdge.main_geom_field
    tile_fields = ("id", "name", "color")
    type_related_name = "organization"
    type_value_field = "organization__organism"
    style_key = "competenceedge"


class SignageManagementEdgeVectorLayer(EdgeVectorLayerMixin, VectorLayer):
    model = models.SignageManagementEdge
    id = f"{models.SignageManagementEdge.__name__.lower()}"
    geom_field = models.SignageManagementEdge.main_geom_field
    tile_fields = ("id", "name", "color")
    type_related_name = "organization"
    type_value_field = "organization__organism"
    style_key = "signagemanagementedge"


class WorkManagementEdgeVectorLayer(EdgeVectorLayerMixin, VectorLayer):
    model = models.WorkManagementEdge
    id = f"{models.WorkManagementEdge.__name__.lower()}"
    geom_field = models.WorkManagementEdge.main_geom_field
    tile_fields = ("id", "name", "color")
    type_related_name = "organization"
    type_value_field = "organization__organism"
    style_key = "workmanagementedge"
