from django.contrib.gis.db import models
from django.db.models import Case, Q, When

from geotrek.common.functions import GeometryN, GeometryType, StartPoint
from geotrek.common.mixins.managers import NoDeleteManager
from geotrek.core.managers import TopologyManager


class TrekOrderedChildManager(models.Manager):
    use_for_related_fields = True

    def get_queryset(self):
        # Select treks foreign keys by default
        qs = super().get_queryset().select_related("parent", "child")
        # Exclude deleted treks
        return qs.exclude(parent__deleted=True).exclude(child__deleted=True)


class TrekManager(TopologyManager):
    def get_queryset(self):
        # Select related fields to optimize queries
        return (
            super()
            .get_queryset()
            .alias(geom_type=GeometryType("geom"))
            .annotate(
                start_point=Case(
                    When(Q(geom_type="POINT"), then="geom"),
                    When(Q(geom_type="LINESTRING"), then=StartPoint("geom")),
                    When(
                        Q(geom_type="MULTILINESTRING"),
                        then=StartPoint(GeometryN("geom", 0)),
                    ),
                    default=None,
                    output_field=models.PointField(),
                )
            )
        )


class WebLinkManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().select_related("category")


class POIManager(NoDeleteManager):
    pass


class ServiceManager(NoDeleteManager):
    pass
