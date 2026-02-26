from django.db.models import F
from vectortiles import VectorLayer

from . import models


class PhysicalEdgeVectorLayer(VectorLayer):
    id = f"{models.PhysicalEdge.__name__.lower()}"  # id for data layer in vector tile
    geom_field = models.PhysicalEdge.main_geom_field  # geom field to consider in qs
    tile_fields = ("id", "name")

    def get_queryset(self):
        return (
            models.PhysicalEdge.objects.existing()
            .select_related("physical_type")
            .annotate(name=F("physical_type__name"))
        )


class LandEdgeVectorLayer(VectorLayer):
    id = f"{models.LandEdge.__name__.lower()}"  # id for data layer in vector tile
    geom_field = models.LandEdge.main_geom_field  # geom field to consider in qs
    tile_fields = ("id", "name")

    def get_queryset(self):
        return (
            models.LandEdge.objects.existing()
            .select_related("land_type")
            .annotate(name=F("land_type__name"))
        )


class CirculationEdgeVectorLayer(VectorLayer):
    id = (
        f"{models.CirculationEdge.__name__.lower()}"  # id for data layer in vector tile
    )
    geom_field = models.CirculationEdge.main_geom_field  # geom field to consider in qs
    tile_fields = ("id", "name")

    def get_queryset(self):
        return (
            models.CirculationEdge.objects.existing()
            .select_related("circulation_type")
            .annotate(name=F("circulation_type__name"))
        )


class CompetenceEdgeVectorLayer(VectorLayer):
    id = f"{models.CompetenceEdge.__name__.lower()}"  # id for data layer in vector tile
    geom_field = models.CompetenceEdge.main_geom_field  # geom field to consider in qs
    tile_fields = ("id", "name")

    def get_queryset(self):
        return (
            models.CompetenceEdge.objects.existing()
            .select_related("organization")
            .annotate(name=F("organization__organism"))
        )


class SignageManagementEdgeVectorLayer(VectorLayer):
    id = f"{models.SignageManagementEdge.__name__.lower()}"  # id for data layer in vector tile
    geom_field = (
        models.SignageManagementEdge.main_geom_field
    )  # geom field to consider in qs
    tile_fields = ("id", "name")

    def get_queryset(self):
        return (
            models.SignageManagementEdge.objects.existing()
            .select_related("organization")
            .annotate(name=F("organization__organism"))
        )


class WorkManagementEdgeVectorLayer(VectorLayer):
    id = f"{models.WorkManagementEdge.__name__.lower()}"  # id for data layer in vector tile
    geom_field = (
        models.WorkManagementEdge.main_geom_field
    )  # geom field to consider in qs
    tile_fields = ("id", "name")

    def get_queryset(self):
        return (
            models.WorkManagementEdge.objects.existing()
            .select_related("organization")
            .annotate(name=F("organization__organism"))
        )
