from django.contrib.gis.db import models
from django.contrib.gis.db.models.functions import Transform
from django.db.models import Value

from geotrek.common.functions import LengthSpheroid
from geotrek.common.mixins.managers import NoDeleteManager


class PathManager(models.Manager):
    # Use this manager when walking through FK/M2M relationships
    use_for_related_fields = True

    def get_queryset(self):
        """Hide all ``Path`` records that are not marked as visible."""
        return super().get_queryset().filter(visible=True)


class PathInvisibleManager(models.Manager):
    use_for_related_fields = True

    def get_queryset(self):
        return super().get_queryset()


class TopologyManager(NoDeleteManager):
    # Use this manager when walking through FK/M2M relationships
    use_for_related_fields = True

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.annotate(
            length_2d=LengthSpheroid(
                Transform("geom", 4326),
                Value('SPHEROID["GRS_1980",6378137,298.257222101]'),
            ),
        )
        return qs


class PathAggregationManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().order_by("order")


class TrailManager(TopologyManager):
    pass
